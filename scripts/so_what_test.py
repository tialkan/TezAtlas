#!/usr/bin/env python3
"""
scripts/so_what_test.py — TezAtlas "Ne Önemi Var?" Testi
                           "So What?" Significance Test

notes/*.md + ARGUMENTS.md + SYNTHESIS.md analiz ederek alanın kanıtladığı şeyi,
bilmediğini ve gerçek dünya etkisini 3 maddede özetler.

Kullanım:
    python3 scripts/so_what_test.py                   # varsayılan
    python3 scripts/so_what_test.py --output SO_WHAT.md

Çıktı: SO_WHAT.md — önem testi raporu
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

# Consensus markers — phrases indicating established findings
_CONSENSUS_MARKERS = re.compile(
    r"\b(kabul görmüştür|yerleşik|genel kabul|konsensüs|yaygın görüş|"
    r"widely accepted|established|consensus|well[- ]known|"
    r"generally agreed|common understanding|mainstream)\b",
    re.IGNORECASE,
)

# Uncertainty markers — phrases indicating unknowns
_UNCERTAINTY_MARKERS = re.compile(
    r"\b(belirsiz|tartışmalı|kesin değil|net değil|hâlâ bilinmiyor|açık soru|"
    r"unclear|uncertain|debat(?:ed|able)|inconclusive|contested|unresolved|"
    r"remains to be seen|open question|not yet understood|unknown)\b",
    re.IGNORECASE,
)

# Impact markers — phrases indicating real-world implications
_IMPACT_MARKERS = re.compile(
    r"\b(etki|katkı|uygulama|politika|pratik|sonuç|değişim|reform|iyileştirme|"
    r"impact|implication|application|policy|practice|reform|improvement|"
    r"real[- ]world|practical|contribut|significant|transform)\b",
    re.IGNORECASE,
)

_CLAIM_PATTERN = re.compile(
    r"\b(bulgu|sonuç|iddia|göstermektedir|kanıtlamaktadır|savunmaktadır|"
    r"finds?|shows?|demonstrates?|argues?|claims?|suggests?|concludes?|"
    r"proves?|reveals?|confirms?)\b",
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

    consensus = []
    uncertainties = []
    impacts = []
    claims = []

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 400:
            continue
        if _CONSENSUS_MARKERS.search(sent):
            consensus.append(sent)
        if _UNCERTAINTY_MARKERS.search(sent):
            uncertainties.append(sent)
        if _IMPACT_MARKERS.search(sent):
            impacts.append(sent)
        if _CLAIM_PATTERN.search(sent):
            claims.append(sent)

    return {
        "file": path.name,
        "title": title,
        "consensus": consensus,
        "uncertainties": uncertainties,
        "impacts": impacts,
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
        arguments.append(claim)
    return arguments


# ── Analysis ──────────────────────────────────────────────────────────────────

def analyze_so_what(
    notes: list[dict],
    arguments: list[str],
    sentez_text: str,
) -> dict:
    """3 temel soruyu cevaplar: ne kanıtlandı, ne bilinmiyor, ne önemi var."""

    # 1. What has been established? (consensus + strong claims)
    all_consensus = []
    for note in notes:
        all_consensus.extend(note["consensus"][:3])

    # Most frequent keywords across all claims → central theme
    all_claim_text = " ".join(
        c for note in notes for c in note["claims"][:5]
    )
    central_keywords = extract_keywords(all_claim_text, 5)

    # 2. What is still unknown?
    all_uncertainties = []
    for note in notes:
        all_uncertainties.extend(note["uncertainties"][:3])

    # 3. Real-world impact
    all_impacts = []
    for note in notes:
        all_impacts.extend(note["impacts"][:3])

    # Sentez contribution
    sentez_sentences = []
    if sentez_text:
        flat = re.sub(r"\n+", " ", sentez_text)
        for sent in re.split(r"(?<=[.!?])\s+", flat):
            sent = sent.strip()
            if 20 < len(sent) < 400:
                if _IMPACT_MARKERS.search(sent) or _CONSENSUS_MARKERS.search(sent):
                    sentez_sentences.append(sent)

    return {
        "central_keywords": central_keywords,
        "consensus_sentences": all_consensus[:8],
        "uncertainty_sentences": all_uncertainties[:8],
        "impact_sentences": all_impacts[:8],
        "sentez_sentences": sentez_sentences[:5],
        "arguments": arguments,
        "total_claims": sum(len(n["claims"]) for n in notes),
    }


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(
    result: dict,
    notes: list[dict],
    output_path: Path,
) -> None:
    kw_str = ", ".join(result["central_keywords"][:5]) if result["central_keywords"] else "—"

    lines = [
        "# \"Ne Önemi Var?\" Testi / \"So What?\" Test",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {len(notes)} kaynak, {result['total_claims']} iddia analiz edildi_",
        "",
        "> Bu rapor, araştırmanızın 3 temel soruya cevabını yapılandırır.",
        "> Claude bu iskeletle çalışırken, cevapları SİZ yazarsınız.",
        "",
        f"**Merkezi kavramlar:** {kw_str}",
        "",
        "---",
        "",
    ]

    # ── Section 1: What has been proven? ──
    lines += [
        "## 1. Bu Alanın Kanıtladığı Şey / What This Field Has Proven",
        "",
        "_Tek cümlelik versiyon:_",
        "",
        "> [ Araştırmanızın alanının yerleşik bulgusu — SİZ yazın ]",
        "",
    ]
    if result["consensus_sentences"]:
        lines += ["**Kaynaklardan konsensüs cümleleri:**", ""]
        for sent in result["consensus_sentences"][:5]:
            lines.append(f"- _{sent}_")
        lines.append("")

    if result["arguments"]:
        lines += ["**Argümanlarınızdan:**", ""]
        for arg in result["arguments"][:5]:
            lines.append(f"- {arg[:100]}")
        lines.append("")

    # ── Section 2: What is still unknown? ──
    lines += [
        "---",
        "",
        "## 2. Hâlâ Bilmediğimizin Dürüst İtirafı / Honest Admission of Unknowns",
        "",
        "_Tek cümlelik versiyon:_",
        "",
        "> [ Bu alanın hâlâ cevaplayamadığı en önemli soru — SİZ yazın ]",
        "",
    ]
    if result["uncertainty_sentences"]:
        lines += ["**Kaynaklardan belirsizlik cümleleri:**", ""]
        for sent in result["uncertainty_sentences"][:5]:
            lines.append(f"- _{sent}_")
        lines.append("")

    # ── Section 3: Real-world impact ──
    lines += [
        "---",
        "",
        "## 3. En Önemli Gerçek Dünya Etkisi / Most Important Real-World Impact",
        "",
        "_Tek cümlelik versiyon:_",
        "",
        "> [ Bu araştırmanın pratik hayatta ne değiştireceği — SİZ yazın ]",
        "",
    ]
    if result["impact_sentences"]:
        lines += ["**Kaynaklardan etki cümleleri:**", ""]
        for sent in result["impact_sentences"][:5]:
            lines.append(f"- _{sent}_")
        lines.append("")

    if result["sentez_sentences"]:
        lines += ["**Sentez'den:**", ""]
        for sent in result["sentez_sentences"][:3]:
            lines.append(f"- _{sent}_")
        lines.append("")

    # ── Self-check ──
    lines += [
        "---",
        "",
        "## Öz-Kontrol / Self-Check",
        "",
        "Yukarıdaki 3 maddeyi yazdıktan sonra kendinize sorun:",
        "",
        "| Soru | ✅/❌ |",
        "|------|------|",
        "| Madde 1 somut mu, genel mi? | |",
        "| Madde 2 dürüst mü, savunmacı mı? | |",
        "| Madde 3 inandırıcı mı, abartılı mı? | |",
        "| 3 madde birlikte tutarlı bir hikaye anlatıyor mu? | |",
        "",
        "## Sonraki Adımlar",
        "",
        "1. 3 maddeyi doldurun ve `/devil-advocate` ile test edin",
        "2. Bu 3 madde tezinizin Giriş ve Sonuç bölümlerinin çekirdeği olacak",
        "3. Güncelle: `python3 scripts/so_what_test.py`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — 'Ne Önemi Var?' Testi"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="SO_WHAT.md",
        help="Çıktı dosyası (varsayılan: SO_WHAT.md)",
    )
    parser.add_argument(
        "--project-dir", metavar="DIR", default=".",
        help="Proje kök dizini",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    notes_dir = project_dir / args.notes
    output_path = project_dir / args.output

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
        c = len(note["consensus"])
        u = len(note["uncertainties"])
        i = len(note["impacts"])
        print(f"   • {path.name}: {c} konsensüs, {u} belirsizlik, {i} etki")

    # Load arguments
    argumanlar_path = project_dir / "ARGUMENTS.md"
    arguments = parse_argumanlar(argumanlar_path)
    print(f"📋 {len(arguments)} argüman yüklendi")

    # Load synthesis
    sentez_path = project_dir / "SYNTHESIS.md"
    sentez_text = ""
    if sentez_path.exists():
        sentez_text = sentez_path.read_text(encoding="utf-8")
        print("📊 SYNTHESIS.md yüklendi")

    print("\n🔍 'Ne Önemi Var?' analizi yapılıyor...")
    result = analyze_so_what(notes, arguments, sentez_text)

    write_report(result, notes, output_path)

    print()
    print(f"{'─' * 50}")
    print(f"  Konsensüs cümlesi    : {len(result['consensus_sentences'])}")
    print(f"  Belirsizlik cümlesi  : {len(result['uncertainty_sentences'])}")
    print(f"  Etki cümlesi         : {len(result['impact_sentences'])}")
    print(f"  Rapor                : {output_path.name}")
    print(f"{'─' * 50}")
    print()
    print("✅ SO_WHAT.md oluşturuldu.")
    print("   3 maddeyi doldurun ve tezinizin çekirdeği olarak kullanın.")


if __name__ == "__main__":
    main()
