#!/usr/bin/env python3
"""
scripts/knowledge_map.py — TezAtlas Bilgi Haritası Üreticisi
                            Knowledge Map Generator

notes/*.md + ARGUMENTS.md analiz ederek merkezi iddia, destek sütunları,
çekişme bölgeleri, sınır soruları ve zorunlu kaynaklar haritası oluşturur.

Kullanım:
    python3 scripts/knowledge_map.py                   # varsayılan
    python3 scripts/knowledge_map.py --output KNOWLEDGE_MAP.md

Çıktı: KNOWLEDGE_MAP.md — yapılandırılmış bilgi haritası
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

# ── Patterns ──────────────────────────────────────────────────────────────────

_WORD_PATTERN = re.compile(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b")

_STOP_WORDS = {
    "için", "ile", "bir", "olan", "olarak", "ancak", "fakat", "daha", "gibi",
    "this", "that", "with", "from", "have", "been", "their", "they", "will",
    "more", "also", "such", "these", "those", "into", "other", "which",
    "when", "where", "what", "were", "than", "then", "some", "each",
    "veya", "yahut", "yani", "hem", "ise", "ama", "öyle", "böyle",
    "kadar", "sonra", "önce", "üzere", "göre", "karşı", "arasında",
}

_SUPPORT_MARKERS = re.compile(
    r"\b(destekle|onaylar|göstermektedir|kanıtlar|doğrular|kabul görmüş|"
    r"support|confirm|demonstrate|show|prove|validate|established|corroborate)\b",
    re.IGNORECASE,
)

_DEBATE_MARKERS = re.compile(
    r"\b(tartışma|karşı|çelişir|eleştirir|zıt|uyuşmazlık|itiraz|"
    r"debate|contention|dispute|controversy|disagree|oppose|challenge|"
    r"counter|conflict|tension|divide)\b",
    re.IGNORECASE,
)

_BOUNDARY_MARKERS = re.compile(
    r"\b(belirsiz|çözülmemiş|kesin değil|bilinmiyor|açık soru|sınırlılık|"
    r"unclear|unresolved|unknown|open question|limitation|boundary|"
    r"not yet|remains to be|further research)\b",
    re.IGNORECASE,
)

_CLAIM_PATTERN = re.compile(
    r"\b(bulgu|sonuç|iddia|göstermektedir|savunmaktadır|"
    r"finds?|shows?|demonstrates?|argues?|claims?|suggests?|concludes?)\b",
    re.IGNORECASE,
)


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    words = _WORD_PATTERN.findall(text.lower())
    freq: dict[str, int] = defaultdict(int)
    for w in words:
        if w not in _STOP_WORDS:
            freq[w] += 1
    return sorted(freq, key=lambda w: -freq[w])[:top_n]


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_note(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    title = path.stem
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Author + Year
    author = ""
    for line in content.splitlines():
        m = re.match(r"^(?:Yazar|Author)\s*:\s*(.+)", line, re.IGNORECASE)
        if m:
            author = m.group(1).strip()
            break

    year = ""
    ym = re.search(r"\b(19[89]\d|20[0-2]\d)\b", content[:500])
    if ym:
        year = ym.group(1)

    # DOI
    doi = ""
    dm = re.search(r"10\.\d{4,9}/\S+", content)
    if dm:
        doi = dm.group(0).rstrip(".,;)")

    text_flat = re.sub(r"\n+", " ", content)
    sentences = re.split(r"(?<=[.!?])\s+", text_flat)

    supports = []
    debates = []
    boundaries = []
    claims = []

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 400:
            continue
        if _SUPPORT_MARKERS.search(sent):
            supports.append(sent)
        if _DEBATE_MARKERS.search(sent):
            debates.append(sent)
        if _BOUNDARY_MARKERS.search(sent):
            boundaries.append(sent)
        if _CLAIM_PATTERN.search(sent):
            claims.append(sent)

    # Citation count proxy: how many other notes reference this one's keywords
    citation_score = len(claims) + len(supports)

    return {
        "file": path.name,
        "title": title,
        "author": author,
        "year": year,
        "doi": doi,
        "supports": supports,
        "debates": debates,
        "boundaries": boundaries,
        "claims": claims,
        "keywords": extract_keywords(content),
        "citation_score": citation_score,
        "content": content,
    }


def parse_argumanlar(path: Path) -> list[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    arguments = []
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        first = parts[0]
        if re.match(r"^(#|No|Num|İddia|Argüman|Claim|Argument)\b", first, re.IGNORECASE):
            continue
        claim = parts[1] if len(parts) > 1 else parts[0]
        if claim and len(claim) >= 5:
            arguments.append(claim)
    return arguments


# ── Analysis ──────────────────────────────────────────────────────────────────

def build_knowledge_map(
    notes: list[dict],
    arguments: list[str],
) -> dict:
    """Bilgi haritası yapısını oluşturur."""

    # 1. Central claim — most frequent keyword cluster
    all_text = " ".join(n["content"][:500] for n in notes)
    central_keywords = extract_keywords(all_text, 5)

    # 2. Support pillars — most established sub-claims
    all_supports = []
    for note in notes:
        for sent in note["supports"][:3]:
            all_supports.append({"sentence": sent, "source": note["file"]})

    # Cluster supports by shared keywords
    pillar_groups: dict[str, list[dict]] = defaultdict(list)
    for s in all_supports:
        kw = extract_keywords(s["sentence"], 3)
        if kw:
            pillar_groups[kw[0]].append(s)

    # Top 5 pillars (by support count)
    pillars = sorted(pillar_groups.items(), key=lambda x: -len(x[1]))[:5]

    # 3. Contention zones — active debates
    all_debates = []
    for note in notes:
        for sent in note["debates"][:3]:
            all_debates.append({"sentence": sent, "source": note["file"]})

    debate_groups: dict[str, list[dict]] = defaultdict(list)
    for d in all_debates:
        kw = extract_keywords(d["sentence"], 3)
        if kw:
            debate_groups[kw[0]].append(d)

    contentions = sorted(debate_groups.items(), key=lambda x: -len(x[1]))[:3]

    # 4. Boundary questions — unresolved issues
    all_boundaries = []
    for note in notes:
        for sent in note["boundaries"][:2]:
            all_boundaries.append({"sentence": sent, "source": note["file"]})

    # 5. Essential reads — highest citation scores
    sorted_notes = sorted(notes, key=lambda n: -n["citation_score"])
    essential = sorted_notes[:3]

    return {
        "central_keywords": central_keywords,
        "pillars": pillars,
        "contentions": contentions,
        "boundaries": all_boundaries[:5],
        "essential_reads": essential,
        "arguments": arguments,
    }


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(
    km: dict,
    notes: list[dict],
    output_path: Path,
) -> None:
    kw_str = ", ".join(km["central_keywords"][:5])

    lines = [
        "# Bilgi Haritası / Knowledge Map",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {len(notes)} kaynak analiz edildi_",
        "",
        "> Bu harita, araştırma alanınızın yapısını tek bakışta gösterir.",
        "",
        "---",
        "",
    ]

    # ── Tree structure ──
    lines += [
        "## Harita Yapısı / Map Structure",
        "",
        "```",
        f"Merkez İddia: [{kw_str}]",
    ]

    # Pillars
    if km["pillars"]:
        lines.append("├── Destek Sütunları")
        for i, (kw, entries) in enumerate(km["pillars"]):
            prefix = "│   ├──" if i < len(km["pillars"]) - 1 else "│   └──"
            lines.append(f"{prefix} {kw} ({len(entries)} kaynak)")
    else:
        lines.append("├── Destek Sütunları: (henüz yeterli veri yok)")

    # Contentions
    if km["contentions"]:
        lines.append("├── Çekişme Bölgeleri")
        for i, (kw, entries) in enumerate(km["contentions"]):
            prefix = "│   ├──" if i < len(km["contentions"]) - 1 else "│   └──"
            lines.append(f"{prefix} {kw} ({len(entries)} kaynak)")
    else:
        lines.append("├── Çekişme Bölgeleri: (belirgin tartışma tespit edilmedi)")

    # Boundaries
    if km["boundaries"]:
        lines.append("├── Sınır Soruları")
        for i, b in enumerate(km["boundaries"][:2]):
            prefix = "│   ├──" if i == 0 else "│   └──"
            short = b["sentence"][:60] + "..." if len(b["sentence"]) > 60 else b["sentence"]
            lines.append(f"{prefix} {short}")
    else:
        lines.append("├── Sınır Soruları: (henüz tespit edilmedi)")

    # Essential reads
    if km["essential_reads"]:
        lines.append("└── Zorunlu Kaynaklar")
        for i, n in enumerate(km["essential_reads"]):
            prefix = "    ├──" if i < len(km["essential_reads"]) - 1 else "    └──"
            lines.append(f"{prefix} {n['title']} ({n['file']})")

    lines += ["```", "", "---", ""]

    # ── Detailed sections ──

    # Pillars detail
    lines += [
        "## Destek Sütunları / Support Pillars",
        "",
        "Alanın etrafında döndüğü yerleşik alt-iddialar:",
        "",
    ]
    if km["pillars"]:
        for kw, entries in km["pillars"]:
            lines += [f"### {kw.title()}", ""]
            for e in entries[:3]:
                lines.append(f"- _{e['source']}:_ {e['sentence'][:150]}")
            lines.append("")
    else:
        lines += ["_(Yeterli destek cümlesi bulunamadı — daha fazla kaynak okuyun)_", ""]

    # Contentions detail
    lines += [
        "---",
        "",
        "## Çekişme Bölgeleri / Contention Zones",
        "",
        "Aktif tartışma alanları:",
        "",
    ]
    if km["contentions"]:
        for kw, entries in km["contentions"]:
            lines += [f"### {kw.title()}", ""]
            for e in entries[:3]:
                lines.append(f"- _{e['source']}:_ {e['sentence'][:150]}")
            lines.append("")
    else:
        lines += ["_(Belirgin tartışma alanı tespit edilmedi)_", ""]

    # Boundaries detail
    lines += [
        "---",
        "",
        "## Sınır Soruları / Boundary Questions",
        "",
        "Çözülmemiş veya belirsiz meseleler:",
        "",
    ]
    if km["boundaries"]:
        for b in km["boundaries"]:
            lines.append(f"- _{b['source']}:_ {b['sentence'][:200]}")
        lines.append("")
    else:
        lines += ["_(Sınır sorusu bulunamadı)_", ""]

    # Essential reads
    lines += [
        "---",
        "",
        "## Yeni Gelenler İçin Zorunlu Kaynaklar / Essential Reads",
        "",
    ]
    for i, n in enumerate(km["essential_reads"], 1):
        doi_str = f" — DOI: {n['doi']}" if n["doi"] else ""
        lines += [
            f"**{i}. {n['title']}**",
            f"- Dosya: `{n['file']}`{doi_str}",
            f"- Yazar: {n['author'] or '—'} ({n['year'] or '—'})",
            f"- İddia gücü: {n['citation_score']} iddia cümlesi",
            "",
        ]

    # Next steps
    lines += [
        "---",
        "",
        "## Sonraki Adımlar",
        "",
        "1. Harita yapısını kendi araştırma sorunuzla karşılaştırın",
        "2. Çekişme bölgelerini `/contradictions` ile derinleştirin",
        "3. Sınır sorularını `/gaps` ile araştırın",
        "4. Güncelle: `python3 scripts/knowledge_map.py`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Bilgi Haritası Üreticisi"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="KNOWLEDGE_MAP.md",
        help="Çıktı dosyası (varsayılan: KNOWLEDGE_MAP.md)",
    )
    parser.add_argument(
        "--project-dir", metavar="DIR", default=".",
        help="Proje kök dizini",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    notes_dir = project_dir / args.notes
    output_path = project_dir / args.output
    argumanlar_path = project_dir / "ARGUMENTS.md"

    if not notes_dir.is_dir():
        print("⚠️  Not dizini bulunamadı:", notes_dir)
        sys.exit(0)

    note_files = sorted(notes_dir.glob("*.md"))
    if not note_files:
        print("ℹ️  notes/ dizininde hiç .md dosyası yok.")
        sys.exit(0)

    print(f"📝 {len(note_files)} not dosyası taranıyor...")
    notes = []
    for path in note_files:
        note = parse_note(path)
        notes.append(note)
        print(f"   • {path.name}: {len(note['supports'])} destek, {len(note['debates'])} tartışma, {len(note['boundaries'])} sınır")

    arguments = parse_argumanlar(argumanlar_path)
    print(f"📋 {len(arguments)} argüman yüklendi")

    print("\n🗺️  Bilgi haritası oluşturuluyor...")
    km = build_knowledge_map(notes, arguments)

    write_report(km, notes, output_path)

    print()
    print(f"{'─' * 50}")
    print(f"  Destek sütunu        : {len(km['pillars'])}")
    print(f"  Çekişme bölgesi      : {len(km['contentions'])}")
    print(f"  Sınır sorusu         : {len(km['boundaries'])}")
    print(f"  Zorunlu kaynak       : {len(km['essential_reads'])}")
    print(f"  Rapor                : {output_path.name}")
    print(f"{'─' * 50}")
    print()
    print("✅ KNOWLEDGE_MAP.md oluşturuldu.")


if __name__ == "__main__":
    main()
