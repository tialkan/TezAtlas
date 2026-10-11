#!/usr/bin/env python3
"""
scripts/saturation_map.py — TezAtlas Semantik Doygunluk Haritası
                            Semantic Saturation Analysis

ARGUMENTS.md'deki her argümanın kaynak kapsama oranını hesaplar.
Hangi argümanların yeterince desteklendiğini, hangilerinin daha fazla
kaynak gerektirdiğini gösterir.

Kullanım:
    python3 scripts/saturation_map.py              # varsayılan: ./
    python3 scripts/saturation_map.py --output SATURATION.md

Çıktı: SATURATION.md — argüman başına kapsama raporu
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


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    words = _WORD_PATTERN.findall(text.lower())
    freq: dict[str, int] = defaultdict(int)
    for w in words:
        if w not in _STOP_WORDS:
            freq[w] += 1
    return sorted(freq, key=lambda w: -freq[w])[:top_n]


# ── ARGUMENTS.md parser ──────────────────────────────────────────────────────

def parse_argumanlar(path: Path) -> list[dict]:
    """
    ARGUMENTS.md tablosunu parse eder.
    Tablo formatı:
    | # | İddia/Argüman | Kaynak | Zıt Görüş | Güç |
    """
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    arguments = []
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "---" in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        # Skip header row
        first = parts[0] if parts else ""
        if re.match(r"^(#|No|Num|İddia|Argüman|Claim|Argument)\b", first, re.IGNORECASE):
            continue
        # Extract claim text (column 1 or 2)
        claim_text = parts[1] if len(parts) > 1 else parts[0]
        if not claim_text or len(claim_text) < 5:
            continue
        # Extract source reference if present (column 2 or 3)
        source_ref = ""
        if len(parts) > 2:
            source_ref = parts[2]

        arguments.append({
            "index": len(arguments) + 1,
            "claim": claim_text,
            "source_ref": source_ref,
            "keywords": extract_keywords(claim_text),
        })
    return arguments


# ── Notes coverage analysis ────────────────────────────────────────────────────

def load_notes(notes_dir: Path) -> list[dict]:
    """notes/*.md dosyalarını yükler."""
    notes = []
    if not notes_dir.is_dir():
        return notes
    for path in sorted(notes_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        keywords = extract_keywords(content, top_n=20)
        notes.append({
            "file": path.name,
            "keywords": set(keywords),
            "content": content,
        })
    return notes


def compute_coverage(argument: dict, notes: list[dict]) -> dict:
    """
    Bir argümanın not dosyaları tarafından ne kadar kapsandığını hesaplar.

    Kapsama skoru:
    - Her not, argümanın anahtar kelimelerini kaç tane içeriyor?
    - Yüksek örtüşme = bu argümanı destekleyen/tartışan kaynak var
    """
    arg_keywords = set(argument["keywords"])
    if not arg_keywords:
        return {"covering_notes": [], "coverage_score": 0, "gap": True}

    covering_notes = []
    for note in notes:
        overlap = arg_keywords & note["keywords"]
        overlap_ratio = len(overlap) / len(arg_keywords)
        if overlap_ratio >= 0.3:  # At least 30% keyword overlap
            covering_notes.append({
                "file": note["file"],
                "overlap": sorted(overlap),
                "ratio": overlap_ratio,
            })

    coverage_score = min(100, int(len(covering_notes) / max(1, len(notes)) * 200))
    # Normalize: 2+ covering notes = 100%
    coverage_score = min(100, len(covering_notes) * 33)

    return {
        "covering_notes": covering_notes,
        "coverage_score": coverage_score,
        "gap": len(covering_notes) == 0,
        "weak": 0 < len(covering_notes) < 2,
    }


def coverage_bar(score: int) -> str:
    filled = score // 10
    bar = "█" * filled + "░" * (10 - filled)
    return f"[{bar}] {score}%"


def coverage_emoji(result: dict) -> str:
    if result["gap"]:
        return "🔴"
    if result["weak"]:
        return "🟡"
    return "🟢"


# ── Report writer ──────────────────────────────────────────────────────────────

def write_saturation_report(
    output_path: Path,
    arguments: list[dict],
    coverage_results: list[dict],
    notes: list[dict],
    total_pdfs: int,
) -> None:
    total_args = len(arguments)
    saturated = sum(1 for r in coverage_results if not r["gap"] and not r["weak"])
    weak = sum(1 for r in coverage_results if r["weak"])
    gaps = sum(1 for r in coverage_results if r["gap"])

    overall_pct = int(saturated / max(1, total_args) * 100)

    lines = [
        "# Semantik Doygunluk Haritası / Semantic Saturation Map",
        "",
        f"_Oluşturulma: {date.today().isoformat()}_",
        "",
        "## Genel Durum",
        "",
        "| Metrik | Değer |",
        "|--------|-------|",
        f"| Toplam argüman | {total_args} |",
        f"| Taranan not dosyası | {len(notes)} |",
        f"| Taranan PDF | {total_pdfs} |",
        f"| 🟢 Yeterince kapsanan | {saturated} |",
        f"| 🟡 Zayıf kapsanan (1 kaynak) | {weak} |",
        f"| 🔴 Kaynak boşluğu | {gaps} |",
        f"| Genel doygunluk | {overall_pct}% |",
        "",
    ]

    # Visual bar
    lines += [
        "```",
        f"Doygunluk: {coverage_bar(overall_pct)}",
        "```",
        "",
    ]

    # Status legend
    lines += [
        "🟢 = 2+ kaynak kapsıyor  |  🟡 = 1 kaynak  |  🔴 = Hiç kaynak yok (boşluk!)",
        "",
        "---",
        "",
        "## Argüman Bazlı Kapsama",
        "",
    ]

    for i, (arg, cov) in enumerate(zip(arguments, coverage_results)):
        emoji = coverage_emoji(cov)
        score = cov["coverage_score"]
        lines += [
            f"### {emoji} Argüman {arg['index']}: {arg['claim'][:80]}{'...' if len(arg['claim']) > 80 else ''}",
            "",
            f"**Kapsama:** {coverage_bar(score)}",
            f"**Anahtar kelimeler:** {', '.join(arg['keywords'][:6])}",
            "",
        ]
        if cov["covering_notes"]:
            lines.append("**Kapsayan kaynaklar:**")
            lines.append("")
            for cn in cov["covering_notes"]:
                overlap_str = ", ".join(cn["overlap"][:5])
                lines.append(
                    f"- `{cn['file']}` — ortak kavramlar: _{overlap_str}_"
                )
            lines.append("")
        else:
            lines += [
                "**⚠️ Bu argümanı destekleyen kaynak notu bulunamadı.**",
                "",
                "Önerilen adımlar:",
                f"1. Bu konuda kaynak ara: `python3 scripts/find_source.py '{arg['keywords'][0] if arg['keywords'] else arg['claim'][:30]}' --output sources/`",
                "2. Kaynağı oku ve notes/ dizinine not ekle",
                "3. Doygunluk haritasını güncelle: `python3 scripts/saturation_map.py`",
                "",
            ]

    # Gap summary
    if gaps > 0:
        lines += [
            "---",
            "",
            "## 🔴 Boşluk Özeti (Kaynak Gereken Argümanlar)",
            "",
            "Aşağıdaki argümanlar için kaynak eksik — yazım fazına geçmeden önce kapatılmalı:",
            "",
        ]
        for arg, cov in zip(arguments, coverage_results):
            if cov["gap"]:
                lines.append(f"- **Argüman {arg['index']}:** {arg['claim'][:100]}")
        lines += [
            "",
            "Bu boşlukları kapatmak için:",
            "```",
            "python3 scripts/find_source.py '<argüman anahtar kelimesi>' --output sources/",
            "python3 scripts/reading_tracker.py sync",
            "```",
            "",
        ]

    lines += [
        "---",
        "",
        "## Güncelleme",
        "",
        "Yeni notlar ekledikten sonra bu raporu güncelle:",
        "```",
        "python3 scripts/saturation_map.py",
        "```",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Semantik Doygunluk Haritası"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="SATURATION.md",
        help="Çıktı dosyası (varsayılan: SATURATION.md)",
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
    sources_dir = project_dir / "sources"

    # Load arguments
    arguments = parse_argumanlar(argumanlar_path)
    if not arguments:
        print("⚠️  ARGUMENTS.md bulunamadı ya da argüman yok.")
        print("💡 Önce ARGUMENTS.md'e argümanlarını ekle.")
        sys.exit(0)

    print(f"📋 {len(arguments)} argüman yüklendi (ARGUMENTS.md)")

    # Load notes
    notes = load_notes(notes_dir)
    print(f"📝 {len(notes)} not dosyası yüklendi")

    # Count PDFs
    total_pdfs = len(list(sources_dir.glob("*.pdf"))) if sources_dir.is_dir() else 0
    print(f"📄 {total_pdfs} PDF kaynakta")
    print()

    # Compute coverage
    print("🔍 Kapsama analizi yapılıyor...")
    coverage_results = []
    for arg in arguments:
        cov = compute_coverage(arg, notes)
        coverage_results.append(cov)
        emoji = coverage_emoji(cov)
        print(f"   {emoji} Argüman {arg['index']}: {cov['coverage_score']}% — {arg['claim'][:50]}...")

    # Write report
    write_saturation_report(output_path, arguments, coverage_results, notes, total_pdfs)

    # Summary
    gaps = sum(1 for r in coverage_results if r["gap"])
    weak = sum(1 for r in coverage_results if r["weak"])
    saturated = len(arguments) - gaps - weak

    print()
    print(f"{'─' * 50}")
    print(f"  🟢 Yeterli kapsama : {saturated}/{len(arguments)}")
    print(f"  🟡 Zayıf kapsama   : {weak}/{len(arguments)}")
    print(f"  🔴 Boşluk          : {gaps}/{len(arguments)}")
    print(f"  Rapor              : {output_path.name}")
    print(f"{'─' * 50}")

    if gaps > 0:
        print(f"\n⚠️  {gaps} argüman için kaynak notu eksik.")
        print("Yazım fazına geçmeden önce bu boşlukları kapat.")
    else:
        print("\n✅ Tüm argümanlar en az bir kaynakla kapsanmış.")


if __name__ == "__main__":
    main()
