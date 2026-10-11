#!/usr/bin/env python3
"""
style_linter.py — TezAtlas Academic Writing Style Linter

Detects:
  - Passive voice density (> 25% threshold warning)
  - Over-hedging chains (3+ hedge words in sequence)
  - Over-claiming language
  - Sentence length variance
  - Turkish equivalents of all patterns

Usage:
  python3 tools/style_linter.py chapter3.md
  python3 tools/style_linter.py --dir draft/ --threshold 0.20
  python3 tools/style_linter.py paper.md --lang tr
  python3 tools/style_linter.py paper.md --json  # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ── Pattern Libraries ──────────────────────────────────────────────────────────

# English passive voice indicators (simplified heuristic: be-verb + past participle)
EN_PASSIVE_PATTERNS = [
    r'\b(is|are|was|were|been|being|be)\s+\w+ed\b',
    r'\b(is|are|was|were)\s+\w+en\b',  # e.g., "was given", "is taken"
    r'\bit\s+(was|has been|is)\s+(found|shown|demonstrated|argued|suggested|noted)\b',
    r'\b(was|were|has been|have been|had been)\s+\w+(ed|en)\b',
]

# Turkish passive indicators (-ldi/-ldi/-ndı/-ndi/-ıldı/-ildi endings on verbs)
TR_PASSIVE_PATTERNS = [
    r'\b\w+(ıldı|ildi|uldu|üldü|ıldığı|ildiği|ndı|ndi|ndu|ndü)\b',
    r'\b\w+(ılmış|ilmiş|ulmuş|ülmüş|nmış|nmiş|nmuş|nmüş)\b',
]

# English over-hedging: single hedge words
EN_HEDGE_WORDS = [
    'perhaps', 'possibly', 'maybe', 'might', 'may', 'could', 'seemingly',
    'apparently', 'arguably', 'presumably', 'somewhat', 'rather', 'fairly',
    'quite', 'generally', 'typically', 'often', 'usually', 'tends to',
    'it seems', 'it appears', 'it would seem', 'it could be',
]

# Turkish over-hedging
TR_HEDGE_WORDS = [
    'belki', 'muhtemelen', 'olasılıkla', 'görünmektedir', 'gibi görünmektedir',
    'olabilir', 'olabilmektedir', 'görülmektedir', 'düşünülmektedir',
    'söylenebilir', 'ifade edilebilir', 'kabul edilebilir', 'değerlendirilebilir',
]

# Over-claiming patterns (English)
EN_OVERCLAIM_PATTERNS = [
    (r'\bdefinitively proves?\b', 'provides evidence for'),
    (r'\bclearly demonstrates?\b', 'suggests' ),
    (r'\bwithout (any )?doubt\b', '(remove or soften)'),
    (r'\bthe first (study|paper|research) ever\b', 'verify this claim'),
    (r'\brevolutionar(y|ily)\b', '(remove — editors dislike this)'),
    (r'\bgroundbreaking\b', '(remove — editors dislike this)'),
    (r'\bundeniably\b', '(soften)'),
    (r'\bobviously\b', '(remove — not obvious to all readers)'),
    (r'\bproves? (that|the)\b', 'provides evidence that'),
]

# Over-claiming patterns (Turkish)
TR_OVERCLAIM_PATTERNS = [
    (r'\bkesinlikle kanıtlamaktadır\b', 'kanıt sunmaktadır'),
    (r'\baçıkça göstermektedir\b', 'göstermektedir / ortaya koymaktadır'),
    (r'\bşüphe götürmez\b', '(yumuşat)'),
    (r'\bilk ve tek\b', 'kaynağını doğrula'),
    (r'\bdevrimsel\b', '(kaldır)'),
    (r'\bkuşkusuz\b', '(yumuşat)'),
]

# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclass
class LintIssue:
    category: str       # passive | hedge | overclaim | sentence_length
    severity: str       # warning | error | info
    line: int
    text: str
    suggestion: str = ""

@dataclass
class LintReport:
    file: str
    word_count: int
    sentence_count: int
    passive_count: int
    passive_rate: float
    hedge_chains: int
    overclaim_count: int
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def score(self) -> int:
        """0-100 style score: 100 = clean, deductions per issue type."""
        deductions = (
            min(30, int(max(0, self.passive_rate - 0.25) * 200)) +  # max 30 for passive
            min(20, self.hedge_chains * 5) +                         # max 20 for hedging
            min(30, self.overclaim_count * 10)                       # max 30 for overclaiming
        )
        return max(0, 100 - deductions)

# ── Linting Functions ──────────────────────────────────────────────────────────

def strip_markdown(text: str) -> str:
    """Remove markdown syntax for cleaner analysis."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)                # bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)                    # italic
    text = re.sub(r'`[^`]+`', '', text)                         # inline code
    text = re.sub(r'```[\s\S]*?```', '', text)                  # code blocks
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # lists
    text = re.sub(r'^\s*\|.+\|.*$', '', text, flags=re.MULTILINE) # tables
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)       # links
    return text


def count_words(text: str) -> int:
    return len(text.split())


def split_sentences(text: str) -> list[str]:
    # Simple sentence splitter for EN + TR
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def detect_passive(text: str, lang: str) -> list[tuple[int, str]]:
    """Returns list of (line_number, matched_text)."""
    patterns = EN_PASSIVE_PATTERNS if lang == "en" else TR_PASSIVE_PATTERNS
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat in patterns:
            for m in re.finditer(pat, line, re.IGNORECASE):
                results.append((i, m.group()))
    return results


def detect_hedge_chains(text: str, lang: str) -> list[tuple[int, str, int]]:
    """Returns list of (line_number, matched_text, chain_length). Only chains of 3+."""
    hedge_words = EN_HEDGE_WORDS if lang == "en" else TR_HEDGE_WORDS
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        found = []
        for hw in hedge_words:
            if re.search(r'\b' + re.escape(hw) + r'\b', line, re.IGNORECASE):
                found.append(hw)
        if len(found) >= 3:
            results.append((i, " + ".join(found[:4]), len(found)))
    return results


def detect_overclaims(text: str, lang: str) -> list[tuple[int, str, str]]:
    """Returns list of (line_number, matched_text, suggestion)."""
    patterns = EN_OVERCLAIM_PATTERNS if lang == "en" else TR_OVERCLAIM_PATTERNS
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat, suggestion in patterns:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                results.append((i, m.group(), suggestion))
    return results


def check_sentence_length(text: str) -> list[tuple[int, int]]:
    """Returns list of (line_number, word_count) for very long sentences (> 60 words)."""
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        sentences = split_sentences(line)
        for s in sentences:
            wc = count_words(s)
            if wc > 60:
                results.append((i, wc))
    return results


# ── Main Linter ────────────────────────────────────────────────────────────────

def lint_file(filepath: Path, lang: str = "en", passive_threshold: float = 0.25) -> LintReport:
    raw = filepath.read_text(encoding="utf-8")
    text = strip_markdown(raw)

    word_count = count_words(text)
    sentences = split_sentences(text)
    sentence_count = len(sentences)

    passives = detect_passive(text, lang)
    hedge_chains = detect_hedge_chains(text, lang)
    overclaims = detect_overclaims(text, lang)
    long_sentences = check_sentence_length(text)

    passive_rate = len(passives) / max(1, sentence_count)

    issues: list[LintIssue] = []

    # Passive summary (per-section, not per-match to avoid noise)
    if passive_rate > passive_threshold:
        issues.append(LintIssue(
            category="passive",
            severity="warning",
            line=0,
            text=f"Pasif çatı oranı: {passive_rate:.0%} (eşik: {passive_threshold:.0%})",
            suggestion="Yöntem bölümü dışında pasif çatıyı azaltın",
        ))

    # Hedge chains
    for lineno, matched, chain_len in hedge_chains:
        issues.append(LintIssue(
            category="hedge",
            severity="warning",
            line=lineno,
            text=f"Çekince zinciri ({chain_len} kelime): {matched}",
            suggestion="Çekince katmanlarını azaltın",
        ))

    # Overclaims
    for lineno, matched, suggestion in overclaims:
        issues.append(LintIssue(
            category="overclaim",
            severity="error",
            line=lineno,
            text=f'Aşırı iddia: "{matched}"',
            suggestion=f"Öneri: {suggestion}",
        ))

    # Long sentences
    for lineno, wc in long_sentences:
        issues.append(LintIssue(
            category="sentence_length",
            severity="info",
            line=lineno,
            text=f"Uzun cümle: {wc} kelime",
            suggestion="İki cümleye bölmeyi düşünün",
        ))

    return LintReport(
        file=str(filepath),
        word_count=word_count,
        sentence_count=sentence_count,
        passive_count=len(passives),
        passive_rate=passive_rate,
        hedge_chains=len(hedge_chains),
        overclaim_count=len(overclaims),
        issues=issues,
    )


def print_report(report: LintReport, verbose: bool = True) -> None:
    status = "✅" if report.score >= 80 else "⚠️" if report.score >= 60 else "❌"

    print(f"\nStil Denetim Raporu — {Path(report.file).name}")
    print("══════════════════════════════════════════════")
    print(f"Kelime: {report.word_count} | Cümle: {report.sentence_count} | Puan: {report.score}/100 {status}")
    print("──────────────────────────────────────────────")
    print(f"Pasif çatı:      {report.passive_rate:.0%}  {'✅' if report.passive_rate <= 0.25 else '⚠️'}")
    print(f"Çekince zinciri: {report.hedge_chains}     {'✅' if report.hedge_chains == 0 else '⚠️'}")
    print(f"Aşırı iddia:     {report.overclaim_count}     {'✅' if report.overclaim_count == 0 else '❌'}")
    print()

    if verbose and report.issues:
        errors = [i for i in report.issues if i.severity == "error"]
        warnings = [i for i in report.issues if i.severity == "warning"]
        infos = [i for i in report.issues if i.severity == "info"]

        if errors:
            print("❌ Hatalar:")
            for issue in errors:
                loc = f"Satır {issue.line}: " if issue.line else ""
                print(f"  {loc}{issue.text}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")

        if warnings:
            print("\n⚠️  Uyarılar:")
            for issue in warnings:
                loc = f"Satır {issue.line}: " if issue.line else ""
                print(f"  {loc}{issue.text}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")

        if infos:
            print("\nℹ️  Bilgi:")
            for issue in infos:
                loc = f"Satır {issue.line}: " if issue.line else ""
                print(f"  {loc}{issue.text}")
    elif not report.issues:
        print("✅ Sorun tespit edilmedi.")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Akademik Yazım Stili Denetleyicisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python3 tools/style_linter.py bolum3.md
  python3 tools/style_linter.py bolum3.md --lang tr
  python3 tools/style_linter.py --dir draft/ --threshold 0.20
  python3 tools/style_linter.py paper.md --json
        """,
    )
    parser.add_argument("file", nargs="?", type=Path, help="Denetlenecek dosya")
    parser.add_argument("--dir", type=Path, help="Dizindeki tüm .md dosyalarını denetle")
    parser.add_argument("--lang", choices=["en", "tr"], default="en",
                        help="Dil / Language (default: en)")
    parser.add_argument("--threshold", type=float, default=0.25,
                        help="Pasif çatı eşiği 0.0-1.0 (varsayılan: 0.25)")
    parser.add_argument("--json", action="store_true", help="JSON çıktısı")
    parser.add_argument("--quiet", action="store_true", help="Yalnızca özet")

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("Dosya veya --dir gerekli")

    files: list[Path] = []
    if args.file:
        files.append(args.file)
    if args.dir:
        files.extend(args.dir.rglob("*.md"))

    reports = [lint_file(f, lang=args.lang, passive_threshold=args.threshold) for f in files]

    if args.json:
        output = [asdict(r) for r in reports]
        # Convert LintIssue objects in issues
        for r_dict in output:
            r_dict['issues'] = [asdict(i) if hasattr(i, '__dataclass_fields__') else i
                                for i in r_dict['issues']]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    for report in reports:
        print_report(report, verbose=not args.quiet)

    if len(reports) > 1:
        avg_score = sum(r.score for r in reports) / len(reports)
        print(f"\n{'═'*46}")
        print(f"Toplam dosya: {len(reports)} | Ortalama puan: {avg_score:.0f}/100")

    # Exit code: 1 if any errors
    has_errors = any(
        any(i.severity == "error" for i in r.issues) for r in reports
    )
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
