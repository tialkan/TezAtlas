#!/usr/bin/env python3
"""
scripts/assumption_killer.py — TezAtlas Varsayım Kırıcı
                                 Assumption Killer

notes/*.md + ARGUMENTS.md tarayarak çoğunluğun paylaştığı ama test etmediği
varsayımları tespit eder. Her varsayım için bağımlı kaynak ve risk analizi sunar.

Kullanım:
    python3 scripts/assumption_killer.py                # varsayılan
    python3 scripts/assumption_killer.py --output ASSUMPTIONS.md

Çıktı: ASSUMPTIONS.md — test edilmemiş varsayımlar raporu
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

# Assumption markers — phrases that signal taken-for-granted beliefs
_ASSUMPTION_MARKERS_TR = [
    r"kabul\s+ed(?:il|er|erek)",
    r"varsay(?:ıl|ar|arak|ım)",
    r"öngörü(?:lmekte|süne|yor)",
    r"doğal\s+olarak",
    r"açıkça",
    r"kuşkusuz",
    r"tartışmasız",
    r"hiç\s+şüphesiz",
    r"herkes(?:çe)?\s+bilinen",
    r"genel\s+kabul",
    r"örtük\s+olarak",
]

_ASSUMPTION_MARKERS_EN = [
    r"assum(?:ed?|ing|ption)",
    r"taken?\s+for\s+granted",
    r"presuppos(?:ed?|ing|ition)",
    r"premise",
    r"implicit(?:ly)?",
    r"obvious(?:ly)?",
    r"clearly",
    r"undoubtedly",
    r"necessarily",
    r"inherent(?:ly)?",
    r"self[- ]?evident",
    r"common(?:ly)?\s+(?:accepted|believed|held|understood)",
    r"widely\s+(?:assumed|believed|accepted)",
    r"goes?\s+without\s+saying",
    r"axiom(?:atic)?",
]

_ASSUMPTION_PATTERN = re.compile(
    "|".join(_ASSUMPTION_MARKERS_TR + _ASSUMPTION_MARKERS_EN),
    re.IGNORECASE,
)

# Claim markers for context
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

    text_flat = re.sub(r"\n+", " ", content)
    sentences = re.split(r"(?<=[.!?])\s+", text_flat)

    # Extract assumption sentences
    assumption_sentences = []
    for sent in sentences:
        sent = sent.strip()
        if 20 < len(sent) < 400 and _ASSUMPTION_PATTERN.search(sent):
            assumption_sentences.append(sent)

    # Extract all claims for dependency analysis
    claims = []
    for sent in sentences:
        sent = sent.strip()
        if 20 < len(sent) < 400 and _CLAIM_PATTERN.search(sent):
            claims.append(sent)

    return {
        "file": path.name,
        "title": title,
        "assumption_sentences": assumption_sentences,
        "claims": claims,
        "keywords": extract_keywords(content),
        "content": content,
    }


def parse_argumanlar(path: Path) -> list[dict]:
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
        if not claim or len(claim) < 5:
            continue
        arguments.append({
            "index": len(arguments) + 1,
            "claim": claim,
            "keywords": extract_keywords(claim),
        })
    return arguments


# ── Analysis ──────────────────────────────────────────────────────────────────

def find_assumptions(
    notes: list[dict],
    arguments: list[dict],
) -> list[dict]:
    """Paylaşılan varsayımları tespit eder ve risk analizi yapar."""
    assumptions = []

    # 1. Collect assumption sentences and group by keyword
    assumption_pool: dict[str, list[dict]] = defaultdict(list)

    for note in notes:
        for sent in note["assumption_sentences"]:
            kws = extract_keywords(sent, 5)
            for kw in kws[:2]:  # Group by top 2 keywords
                assumption_pool[kw].append({
                    "sentence": sent,
                    "source": note["file"],
                    "title": note["title"],
                })

    # 2. Identify shared assumptions (mentioned in 2+ sources)
    for kw, entries in sorted(assumption_pool.items(), key=lambda x: -len(x[1])):
        unique_sources = set(e["source"] for e in entries)
        if len(unique_sources) >= 2:
            # Find which arguments depend on this assumption
            dependent_args = []
            for arg in arguments:
                if kw in arg["keywords"]:
                    dependent_args.append(arg)

            assumptions.append({
                "keyword": kw,
                "entries": entries[:5],
                "source_count": len(unique_sources),
                "dependent_args": dependent_args,
                "shared": True,
            })

    # 3. Also flag single-source assumptions that affect many claims
    for note in notes:
        for sent in note["assumption_sentences"]:
            kws = extract_keywords(sent, 3)
            # Check if this assumption underlies multiple arguments
            dependent = []
            for arg in arguments:
                overlap = set(kws) & set(arg["keywords"])
                if len(overlap) >= 2:
                    dependent.append(arg)
            if len(dependent) >= 2 and not any(
                a["keyword"] in kws for a in assumptions
            ):
                assumptions.append({
                    "keyword": kws[0] if kws else "—",
                    "entries": [{"sentence": sent, "source": note["file"], "title": note["title"]}],
                    "source_count": 1,
                    "dependent_args": dependent,
                    "shared": False,
                })

    # Sort by risk: shared assumptions that affect many arguments first
    assumptions.sort(key=lambda a: -(a["source_count"] * 2 + len(a["dependent_args"])))

    return assumptions[:10]  # Top 10


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(
    assumptions: list[dict],
    notes: list[dict],
    arguments: list[dict],
    output_path: Path,
) -> None:
    lines = [
        "# Varsayım Analizi / Assumption Analysis",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {len(notes)} not, {len(arguments)} argüman tarandı_",
        "",
        "> Test edilmemiş varsayımlar araştırmanın en büyük kör noktasıdır.",
        "> Bu rapor, kaynaklarınızın paylaştığı ama sorgulamadığı varsayımları listeler.",
        "",
        "---",
        "",
    ]

    if not assumptions:
        lines += [
            "## Sonuç",
            "",
            "✅ Belirgin paylaşılan varsayım tespit edilmedi.",
            "",
            "Bu şu anlama gelebilir:",
            "- Kaynaklarınız varsayımlarını açıkça belirtmiyor",
            "- Daha fazla kaynak okuyup bu raporu güncelleyin",
            "- `/devil-advocate` ile argümanlarınızı test edin",
            "",
        ]
    else:
        lines += [
            f"## Tespit Edilen Varsayımlar: {len(assumptions)}",
            "",
        ]

        for i, a in enumerate(assumptions, 1):
            shared_tag = "🔴 PAYLAŞILAN" if a["shared"] else "🟡 TEKİL"
            dep_count = len(a["dependent_args"])

            lines += [
                f"### {shared_tag} Varsayım {i}: \"{a['keyword']}\"",
                "",
                f"**Kaynak sayısı:** {a['source_count']}",
                f"**Bağımlı argüman sayısı:** {dep_count}",
                "",
                "**Varsayım ifadeleri:**",
                "",
            ]

            for e in a["entries"][:3]:
                lines += [
                    f"- _{e['source']}:_",
                    f"  > {e['sentence'][:200]}",
                    "",
                ]

            if a["dependent_args"]:
                lines += [
                    "**Bu varsayıma bağımlı argümanlar:**",
                    "",
                ]
                for arg in a["dependent_args"][:3]:
                    lines.append(f"- Argüman {arg['index']}: {arg['claim'][:80]}")
                lines.append("")

            lines += [
                "**Yanlış çıkarsa ne olur?**",
                "",
                "> [ Bu varsayım çürütülürse hangi argümanlarınız çöker? — SİZ değerlendirin ]",
                "",
                "---",
                "",
            ]

    # Summary
    shared_count = sum(1 for a in assumptions if a["shared"])
    lines += [
        "## Özet",
        "",
        "| Metrik | Değer |",
        "|--------|-------|",
        f"| Toplam varsayım | {len(assumptions)} |",
        f"| Paylaşılan (2+ kaynak) | {shared_count} |",
        f"| Tekil | {len(assumptions) - shared_count} |",
        "",
        "## Sonraki Adımlar",
        "",
        "1. Her varsayım için \"yanlış çıkarsa\" sorusunu cevaplayın",
        "2. Yüksek riskli varsayımları `/devil-advocate` ile test edin",
        "3. Varsayımları açıkça belirten alternatif kaynaklar arayın",
        "4. Güncelle: `python3 scripts/assumption_killer.py`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Varsayım Kırıcı"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="ASSUMPTIONS.md",
        help="Çıktı dosyası (varsayılan: ASSUMPTIONS.md)",
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
        print(f"   • {path.name}: {len(note['assumption_sentences'])} varsayım cümlesi")

    arguments = parse_argumanlar(argumanlar_path)
    print(f"📋 {len(arguments)} argüman yüklendi")

    print("\n🔍 Varsayım analizi yapılıyor...")
    assumptions = find_assumptions(notes, arguments)

    write_report(assumptions, notes, arguments, output_path)

    shared_count = sum(1 for a in assumptions if a["shared"])

    print()
    print(f"{'─' * 50}")
    print(f"  Toplam varsayım      : {len(assumptions)}")
    print(f"  Paylaşılan           : {shared_count}")
    print(f"  Tekil                : {len(assumptions) - shared_count}")
    print(f"  Rapor                : {output_path.name}")
    print(f"{'─' * 50}")

    if assumptions:
        print(f"\n⚠️  {len(assumptions)} test edilmemiş varsayım tespit edildi.")
        print("📋 ASSUMPTIONS.md dosyasını incele ve risk değerlendirmesi yap.")
    else:
        print("\n✅ Belirgin varsayım tespit edilmedi.")


if __name__ == "__main__":
    main()
