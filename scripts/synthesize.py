#!/usr/bin/env python3
"""
scripts/synthesize.py — TezAtlas Çok Kaynaklı Sentez Üreticisi
                        Multi-Source Synthesis Generator

notes/*.md dosyalarını ARGUMENTS.md ile birleştirerek SYNTHESIS.md üretir.
Her argüman için destekleyen, karşı çıkan ve nüanslı kaynakları yapılandırır.
Claude Code'un sentez yazmasına hazır bir iskelet sunar.

Kullanım:
    python3 scripts/synthesize.py                  # SYNTHESIS.md üret
    python3 scripts/synthesize.py --argument 3     # sadece argüman #3 için
    python3 scripts/synthesize.py --output custom.md

Çıktı: SYNTHESIS.md — argüman başına kaynak-görüş matrisi
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

# ── Helpers ───────────────────────────────────────────────────────────────────

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
    r"\b(destekle|onaylar|göstermektedir|kanıtlar|bulmuştur|doğrular|"
    r"support|confirm|demonstrate|show|prove|validate|corroborate)\b",
    re.IGNORECASE,
)
_OPPOSE_MARKERS = re.compile(
    r"\b(karşı|çelişir|reddeder|eleştirir|çürütür|zıt|olumsuz|"
    r"against|oppose|refute|challenge|contradict|dispute|counter)\b",
    re.IGNORECASE,
)
_NUANCE_MARKERS = re.compile(
    r"\b(ancak|bununla birlikte|öte yandan|sınırlı|kısmen|koşullu|"
    r"however|but|although|partly|partially|conditional|limited|nuance)\b",
    re.IGNORECASE,
)


def extract_keywords(text: str, top_n: int = 12) -> set[str]:
    from collections import Counter
    words = _WORD_PATTERN.findall(text.lower())
    freq = Counter(w for w in words if w not in _STOP_WORDS)
    return {w for w, _ in freq.most_common(top_n)}


def extract_key_sentences(text: str, max_sentences: int = 3) -> list[str]:
    """Metinden en önemli iddia cümlelerini çıkarır."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    claim_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 30 or len(s) > 300:
            continue
        if (_SUPPORT_MARKERS.search(s) or _OPPOSE_MARKERS.search(s)
                or _NUANCE_MARKERS.search(s)):
            claim_sentences.append(s)
    return claim_sentences[:max_sentences]


# ── Parsers ────────────────────────────────────────────────────────────────────

def parse_note(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    title = path.stem
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    doi = ""
    doi_match = re.search(r"10\.\d{4,9}/\S+", content)
    if doi_match:
        doi = doi_match.group(0).rstrip(".,;)")

    return {
        "file": path.name,
        "title": title,
        "doi": doi,
        "keywords": extract_keywords(content),
        "key_sentences": extract_key_sentences(content),
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
        if re.match(r"^(#|No|Num|İddia|Argüman|Claim)\b", first, re.IGNORECASE):
            continue
        claim = parts[1] if len(parts) > 1 else parts[0]
        if not claim or len(claim) < 5:
            continue
        arguments.append({
            "index": len(arguments) + 1,
            "claim": claim,
            "source_ref": parts[2] if len(parts) > 2 else "",
            "counter": parts[3] if len(parts) > 3 else "",
            "keywords": extract_keywords(claim),
        })
    return arguments


# ── Matching ───────────────────────────────────────────────────────────────────

def classify_note_stance(note: dict, argument: dict) -> str:
    """
    Notun argümana göre duruşunu tespit eder: support / oppose / nuance / neutral
    """
    arg_kw = argument["keywords"]
    note_kw = note["keywords"]
    overlap = arg_kw & note_kw
    if len(overlap) < 2:
        return "unrelated"

    # Check sentences for stance markers
    support_count = 0
    oppose_count = 0
    nuance_count = 0

    for sent in note["key_sentences"]:
        if _SUPPORT_MARKERS.search(sent):
            support_count += 1
        if _OPPOSE_MARKERS.search(sent):
            oppose_count += 1
        if _NUANCE_MARKERS.search(sent):
            nuance_count += 1

    # Also check full content briefly
    snippet = note["content"][:800]
    if _OPPOSE_MARKERS.search(snippet):
        oppose_count += 1
    if _SUPPORT_MARKERS.search(snippet):
        support_count += 1

    if oppose_count > support_count:
        return "oppose"
    if nuance_count > 0 and support_count > 0:
        return "nuance"
    if support_count > 0:
        return "support"
    if oppose_count > 0:
        return "oppose"
    if len(overlap) >= 3:
        return "related"
    return "unrelated"


def match_notes_to_argument(argument: dict, notes: list[dict]) -> dict:
    """Bir argüman için ilgili notları destekleyen/karşı/nüanslı olarak sınıflar."""
    categories: dict[str, list[dict]] = defaultdict(list)
    for note in notes:
        stance = classify_note_stance(note, argument)
        if stance != "unrelated":
            categories[stance].append(note)
    return dict(categories)


# ── Report writer ──────────────────────────────────────────────────────────────

def write_synthesis_report(
    output_path: Path,
    arguments: list[dict],
    notes: list[dict],
    target_argument: int | None = None,
) -> None:
    total_notes = len(notes)
    total_args = len(arguments)

    lines = [
        "# Çok Kaynaklı Sentez / Multi-Source Synthesis",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {total_notes} not, {total_args} argüman_",
        "",
        "> **Claude için sentez kılavuzu:**",
        "> Bu dosya, her argüman için kaynak-görüş matrisini gösterir.",
        "> Her bölüm için:",
        "> 1. Destekleyen kaynakları birleştir (ortak bulgular neler?)",
        "> 2. Karşı görüşleri güçlendir (en güçlü itiraz nedir?)",
        "> 3. Nüanslı/sınırlı bulguları entegre et",
        "> 4. SYNTHESIS paragrafını yaz: 'Bu kaynaklar bütünüyle şunu gösteriyor...'",
        "",
        "---",
        "",
    ]

    args_to_process = (
        [a for a in arguments if a["index"] == target_argument]
        if target_argument
        else arguments
    )

    for arg in args_to_process:
        matched = match_notes_to_argument(arg, notes)

        support_notes = matched.get("support", [])
        oppose_notes = matched.get("oppose", [])
        nuance_notes = matched.get("nuance", [])
        related_notes = matched.get("related", [])

        all_matched = support_notes + oppose_notes + nuance_notes + related_notes
        coverage_emoji = "🟢" if len(support_notes) >= 2 else ("🟡" if all_matched else "🔴")

        lines += [
            f"## {coverage_emoji} Argüman {arg['index']}: {arg['claim'][:80]}{'...' if len(arg['claim']) > 80 else ''}",
            "",
            f"**Anahtar kavramlar:** {', '.join(sorted(arg['keywords'])[:6])}",
            f"**Kapsama:** {len(support_notes)} destekleyen | {len(oppose_notes)} karşı | {len(nuance_notes)} nüanslı | {len(related_notes)} ilgili",
            "",
        ]

        if support_notes:
            lines += ["### ✅ Destekleyen Kaynaklar", ""]
            for n in support_notes:
                doi_link = f"https://doi.org/{n['doi']}" if n["doi"] else ""
                lines.append(f"**{n['title']}** (`{n['file']}`)")
                if doi_link:
                    lines.append(f"DOI: {doi_link}")
                for sent in n["key_sentences"]:
                    lines.append(f"> {sent}")
                lines.append("")

        if oppose_notes:
            lines += ["### ❌ Karşı Görüşler", ""]
            for n in oppose_notes:
                doi_link = f"https://doi.org/{n['doi']}" if n["doi"] else ""
                lines.append(f"**{n['title']}** (`{n['file']}`)")
                if doi_link:
                    lines.append(f"DOI: {doi_link}")
                for sent in n["key_sentences"]:
                    lines.append(f"> {sent}")
                lines.append("")

        if nuance_notes:
            lines += ["### 🔶 Nüanslı / Koşullu Bulgular", ""]
            for n in nuance_notes:
                lines.append(f"**{n['title']}** (`{n['file']}`)")
                for sent in n["key_sentences"]:
                    lines.append(f"> {sent}")
                lines.append("")

        if related_notes:
            lines += ["### 📎 İlgili (Duruş Belirsiz)", ""]
            for n in related_notes:
                lines.append(f"- `{n['file']}`: {n['title']}")
            lines.append("")

        if not all_matched:
            lines += [
                "### ⚠️ Bu argüman için not bulunamadı",
                "",
                "Önerilen adımlar:",
                f"1. Kaynak ara: `python3 scripts/find_source.py '{list(arg['keywords'])[0] if arg['keywords'] else arg['claim'][:30]}' --output sources/`",
                "2. Kaynağı oku ve notes/ dizinine not ekle",
                "3. Sentezi güncelle: `python3 scripts/synthesize.py`",
                "",
            ]

        # Synthesis prompt for Claude
        lines += [
            "### 📝 Sentez Alanı (Claude burayı dolduracak)",
            "",
            "_Bu kaynaklar bütünüyle şunu gösteriyor:_",
            "",
            "> [ Sentez paragrafı buraya yazılacak ]",
            "",
            "_Temel gerilimler/çelişkiler:_",
            "",
            "> [ Açık sorular ve çözümlenmemiş anlaşmazlıklar ]",
            "",
            "---",
            "",
        ]

    # Coverage summary
    if not target_argument:
        lines += [
            "## Kapsama Özeti",
            "",
            "| Argüman | Destekleyen | Karşı | Nüanslı | Toplam |",
            "|---------|-------------|-------|---------|--------|",
        ]
        for arg in arguments:
            matched = match_notes_to_argument(arg, notes)
            s = len(matched.get("support", []))
            o = len(matched.get("oppose", []))
            n = len(matched.get("nuance", []))
            total = s + o + n + len(matched.get("related", []))
            emoji = "🟢" if s >= 2 else ("🟡" if total > 0 else "🔴")
            lines.append(f"| {emoji} Argüman {arg['index']} | {s} | {o} | {n} | {total} |")

        lines += [
            "",
            "## Sonraki Adımlar",
            "",
            "1. Her sentez alanına (`>`) tıkla ve paragraf yaz",
            "2. Karşı görüşleri SAVUNMA_ZIRHI.md ile karşılaştır",
            "3. Kırmızı argümanlar için kaynak ara ve not ekle",
            "4. Tamamlandığında Phase 5 (Yazım) için hazırsın",
            "",
        ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Çok Kaynaklı Sentez Üreticisi"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="SYNTHESIS.md",
        help="Çıktı dosyası (varsayılan: SYNTHESIS.md)",
    )
    parser.add_argument(
        "--argument", metavar="N", type=int,
        help="Sadece belirtilen argüman için sentez üret",
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

    # Load arguments
    arguments = parse_argumanlar(argumanlar_path)
    if not arguments:
        print("⚠️  ARGUMENTS.md bulunamadı ya da argüman yok.")
        print("💡 Önce ARGUMENTS.md'e argümanlarını ekle.")
        sys.exit(0)
    print(f"📋 {len(arguments)} argüman yüklendi")

    # Load notes
    notes = []
    if notes_dir.is_dir():
        for path in sorted(notes_dir.glob("*.md")):
            notes.append(parse_note(path))
    print(f"📝 {len(notes)} not dosyası yüklendi")

    if not notes:
        print()
        print("ℹ️  notes/ dizininde not bulunamadı.")
        print("💡 Kaynakları okuyup notlarını notes/ dizinine ekle.")
        print("   Ardından sentezi üret: python3 scripts/synthesize.py")
        # Still generate skeleton
        print("   (Şimdi iskelet rapor üretiliyor...)")

    # Generate report
    write_synthesis_report(output_path, arguments, notes, args.argument)

    # Stats
    matched_counts = [
        len(list(match_notes_to_argument(a, notes).values()))
        for a in arguments
    ]
    covered = sum(1 for c in matched_counts if c > 0)

    print()
    print(f"{'─' * 50}")
    print(f"  Kapsanan argüman   : {covered}/{len(arguments)}")
    print(f"  Kapsanmayan        : {len(arguments) - covered}/{len(arguments)}")
    print(f"  Çıktı              : {output_path.name}")
    print(f"{'─' * 50}")
    print()
    print("✅ SYNTHESIS.md oluşturuldu.")
    print("   Her 📝 Sentez Alanı için Claude ile çalış.")


if __name__ == "__main__":
    main()
