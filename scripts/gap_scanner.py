#!/usr/bin/env python3
"""
scripts/gap_scanner.py — TezAtlas Araştırma Boşluğu Tarayıcısı
                          Research Gap Scanner

notes/*.md + ARGUMENTS.md analiz ederek cevaplanmamış araştırma sorularını,
eksik perspektifleri ve metodoloji boşluklarını tespit eder.

Kullanım:
    python3 scripts/gap_scanner.py                    # varsayılan
    python3 scripts/gap_scanner.py --output GAPS.md

Çıktı: GAPS.md — araştırma boşlukları raporu
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

# Gap indicator patterns — phrases that signal unanswered questions
_GAP_MARKERS_TR = [
    r"henüz\s+(?:yeterince\s+)?(?:araştırılmamış|incelenmemiş|çalışılmamış)",
    r"eksik(?:tir|liği|lik)",
    r"daha fazla araştırma",
    r"yetersiz\s+(?:çalışma|veri|kanıt)",
    r"açık soru",
    r"sınırlı\s+(?:sayıda|veri|kanıt|araştırma)",
    r"gelecek(?:te|teki)\s+(?:araştırma|çalışma)",
    r"boşluk",
    r"belirsiz(?:lik)?",
    r"tartışmalı",
]

_GAP_MARKERS_EN = [
    r"under[- ]?researched",
    r"under[- ]?explored",
    r"under[- ]?studied",
    r"gap\s+in\s+(?:the\s+)?literature",
    r"further\s+research\s+(?:is\s+)?needed",
    r"remain[s]?\s+unclear",
    r"limited\s+(?:evidence|data|research|studies)",
    r"open\s+question",
    r"little\s+(?:is\s+)?known",
    r"future\s+(?:research|studies|work)",
    r"scarcity\s+of",
    r"lack[s]?\s+of\s+(?:evidence|data|research)",
    r"insufficient\s+(?:evidence|data)",
    r"inconclusive",
    r"contested",
    r"debat(?:ed|able)",
]

_GAP_PATTERN = re.compile(
    "|".join(_GAP_MARKERS_TR + _GAP_MARKERS_EN),
    re.IGNORECASE,
)

# Question patterns
_QUESTION_PATTERN = re.compile(r"[^.!?]*\?")

# Methodology mentions
_METHOD_KEYWORDS = re.compile(
    r"\b(nitel|nicel|karma|deney|anket|görüşme|içerik analizi|söylem|"
    r"qualitative|quantitative|mixed[- ]method|experiment|survey|interview|"
    r"case study|ethnograph|grounded theory|systematic review|meta[- ]analysis|"
    r"longitudinal|cross[- ]sectional|regression|correlation)\b",
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

    # Extract gap sentences
    gap_sentences = []
    for sent in sentences:
        sent = sent.strip()
        if 20 < len(sent) < 400 and _GAP_PATTERN.search(sent):
            gap_sentences.append(sent)

    # Extract questions
    questions = []
    for m in _QUESTION_PATTERN.finditer(content):
        q = m.group(0).strip()
        if 15 < len(q) < 300:
            questions.append(q)

    # Extract methodology mentions
    methods = set()
    for m in _METHOD_KEYWORDS.finditer(content):
        methods.add(m.group(0).lower())

    return {
        "file": path.name,
        "title": title,
        "keywords": extract_keywords(content),
        "gap_sentences": gap_sentences,
        "questions": questions,
        "methods": sorted(methods),
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
        # Also skip if claim column looks like a header
        if re.match(r"^(İddia|Argüman|Claim|Argument|Kaynak|Source)\b", claim, re.IGNORECASE):
            continue
        if not claim or len(claim) < 5:
            continue
        arguments.append({
            "index": len(arguments) + 1,
            "claim": claim,
            "keywords": extract_keywords(claim),
        })
    return arguments


# ── Gap analysis ──────────────────────────────────────────────────────────────

def analyze_gaps(
    notes: list[dict],
    arguments: list[dict],
) -> dict:
    """Kapsamlı boşluk analizi yapar."""

    # 1. Explicit gaps: sentences where authors mention limitations
    explicit_gaps = []
    for note in notes:
        for sent in note["gap_sentences"]:
            explicit_gaps.append({
                "source": note["file"],
                "sentence": sent,
            })

    # 2. Open questions found in source notes
    open_questions = []
    for note in notes:
        for q in note["questions"][:3]:  # max 3 per note
            open_questions.append({
                "source": note["file"],
                "question": q,
            })

    # 3. Coverage gaps: arguments without supporting notes
    all_note_keywords = set()
    for note in notes:
        all_note_keywords.update(note["keywords"])

    argument_gaps = []
    for arg in arguments:
        arg_kw = set(arg["keywords"])
        overlap = arg_kw & all_note_keywords
        coverage = len(overlap) / max(1, len(arg_kw))
        if coverage < 0.4:
            argument_gaps.append({
                "argument": arg,
                "coverage": coverage,
                "missing_keywords": sorted(arg_kw - all_note_keywords),
            })

    # 4. Methodology gaps: what methods are NOT represented?
    all_methods = set()
    for note in notes:
        all_methods.update(note["methods"])

    common_methods = {
        "qualitative", "quantitative", "mixed-method", "survey",
        "interview", "case study", "experiment", "meta-analysis",
        "nitel", "nicel", "karma", "anket", "görüşme",
    }
    missing_methods = sorted(common_methods - all_methods)

    # 5. Temporal gaps: check if sources span a narrow time range
    # (detected by the slash command prompt, not here)

    return {
        "explicit_gaps": explicit_gaps,
        "open_questions": open_questions,
        "argument_gaps": argument_gaps,
        "missing_methods": missing_methods,
    }


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(
    result: dict,
    notes: list[dict],
    arguments: list[dict],
    output_path: Path,
) -> None:
    total_gaps = (
        len(result["explicit_gaps"])
        + len(result["argument_gaps"])
        + (1 if result["missing_methods"] else 0)
    )

    lines = [
        "# Araştırma Boşlukları Raporu / Research Gap Report",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {len(notes)} not, {len(arguments)} argüman analiz edildi, {total_gaps} boşluk bulundu_",
        "",
        "> Bu rapor, mevcut kaynakların cevaplayamadığı soruları ve eksik perspektifleri gösterir.",
        "> Her boşluk bir araştırma fırsatıdır — tezin katkısını güçlendirebilir.",
        "",
        "---",
        "",
    ]

    # ── 1. Explicit gaps from literature ──
    lines += [
        "## 1. Yazarların Belirttiği Boşluklar",
        "",
        "Kaynak yazarlarının kendilerinin işaret ettiği eksiklikler ve açık sorular:",
        "",
    ]
    if result["explicit_gaps"]:
        for i, g in enumerate(result["explicit_gaps"][:10], 1):
            lines += [
                f"**{i}.** _{g['source']}_",
                f"> {g['sentence']}",
                "",
            ]
    else:
        lines += ["_(Kaynaklar açık boşluk belirtmiyor — daha fazla kaynak okuyun)_", ""]

    # ── 2. Open questions ──
    lines += [
        "---",
        "",
        "## 2. Cevaplanmamış Araştırma Soruları",
        "",
    ]
    if result["open_questions"]:
        for i, q in enumerate(result["open_questions"][:10], 1):
            lines += [
                f"**{i}.** _{q['source']}_",
                f"> {q['question']}",
                "",
            ]
    else:
        lines += ["_(Kaynaklarda açık soru bulunamadı)_", ""]

    # ── 3. Argument coverage gaps ──
    lines += [
        "---",
        "",
        "## 3. Argüman Kapsama Boşlukları",
        "",
        "ARGUMENTS.md'deki bu iddialar yeterli kaynak desteğine sahip değil:",
        "",
    ]
    if result["argument_gaps"]:
        for gap in result["argument_gaps"]:
            arg = gap["argument"]
            pct = int(gap["coverage"] * 100)
            lines += [
                f"### 🔴 Argüman {arg['index']}: {arg['claim'][:80]}",
                "",
                f"- **Kapsama:** {pct}%",
                f"- **Eksik kavramlar:** {', '.join(gap['missing_keywords'][:5])}",
                f"- **Öneri:** Bu kavramlarla kaynak ara: `python3 scripts/find_source.py '{gap['missing_keywords'][0] if gap['missing_keywords'] else arg['claim'][:30]}'`",
                "",
            ]
    else:
        lines += ["✅ Tüm argümanlar en az minimal düzeyde kapsanmış.", ""]

    # ── 4. Methodology gaps ──
    lines += [
        "---",
        "",
        "## 4. Metodoloji Boşlukları",
        "",
    ]
    all_methods_in_notes = set()
    for note in notes:
        all_methods_in_notes.update(note["methods"])

    if all_methods_in_notes:
        lines += [
            f"**Mevcut metodolojiler:** {', '.join(sorted(all_methods_in_notes))}",
            "",
        ]
    if result["missing_methods"]:
        lines += [
            f"**Temsil edilmeyen metodolojiler:** {', '.join(result['missing_methods'])}",
            "",
            "Bu yöntemlerle yapılmış çalışmaları dahil etmek perspektif çeşitliliğini artırır.",
            "",
        ]
    else:
        lines += ["✅ Metodoloji çeşitliliği yeterli görünüyor.", ""]

    # ── Summary ──
    lines += [
        "---",
        "",
        "## Özet / Summary",
        "",
        "| Boşluk Türü | Sayı |",
        "|-------------|------|",
        f"| Yazar belirtmesi | {len(result['explicit_gaps'])} |",
        f"| Açık soru | {len(result['open_questions'])} |",
        f"| Argüman boşluğu | {len(result['argument_gaps'])} |",
        f"| Metodoloji boşluğu | {len(result['missing_methods'])} |",
        "",
        "## Sonraki Adımlar",
        "",
        "1. En kritik boşlukları kendi araştırma katkın olarak değerlendir",
        "2. Eksik argümanlar için kaynak ara: `python3 scripts/find_source.py`",
        "3. Boşlukları ARGUMENTS.md'e katkı olarak kaydet",
        "4. Güncelle: `python3 scripts/gap_scanner.py`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Araştırma Boşluğu Tarayıcısı"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="GAPS.md",
        help="Çıktı dosyası (varsayılan: GAPS.md)",
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
        print("💡 Önce kaynakları oku ve notlarını notes/ klasörüne kaydet.")
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
        print(f"   • {path.name}: {len(note['gap_sentences'])} boşluk cümlesi, {len(note['questions'])} soru")

    arguments = parse_argumanlar(argumanlar_path)
    print(f"📋 {len(arguments)} argüman yüklendi")

    print("\n🔍 Boşluk analizi yapılıyor...")
    result = analyze_gaps(notes, arguments)

    write_report(result, notes, arguments, output_path)

    total_gaps = (
        len(result["explicit_gaps"])
        + len(result["argument_gaps"])
    )

    print()
    print(f"{'─' * 50}")
    print(f"  Yazar belirtmesi     : {len(result['explicit_gaps'])}")
    print(f"  Açık soru            : {len(result['open_questions'])}")
    print(f"  Argüman boşluğu      : {len(result['argument_gaps'])}")
    print(f"  Metodoloji boşluğu   : {len(result['missing_methods'])}")
    print(f"  Rapor                : {output_path.name}")
    print(f"{'─' * 50}")

    if total_gaps > 0:
        print(f"\n⚠️  {total_gaps} boşluk tespit edildi.")
        print("📋 GAPS.md dosyasını incele ve katkı fırsatlarını değerlendir.")
    else:
        print("\n✅ Belirgin boşluk tespit edilmedi.")


if __name__ == "__main__":
    main()
