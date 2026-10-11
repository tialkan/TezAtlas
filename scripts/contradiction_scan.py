#!/usr/bin/env python3
"""
scripts/contradiction_scan.py — TezAtlas Çapraz Kaynak Çelişki Tarayıcısı
                                Cross-Source Contradiction Scanner

notes/*.md dosyalarını tarar, zıt iddiaları ve anlaşmazlıkları tespit eder.
Claude Code'un analiz edebilmesi için yapılandırılmış bir rapor üretir.

Kullanım:
    python3 scripts/contradiction_scan.py               # varsayılan: ./notes/
    python3 scripts/contradiction_scan.py --notes notes/
    python3 scripts/contradiction_scan.py --output CONTRADICTIONS.md

Çıktı: CONTRADICTIONS.md — Claude'un incelemesi için çelişki adayları
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

# ── Claim extraction patterns ─────────────────────────────────────────────────
# We look for sentences with epistemic markers that indicate a finding or claim

_CLAIM_MARKERS_TR = [
    r"\bbulgu\b", r"\bsonuç\b", r"\biddia\b", r"\böne sürmektedir\b",
    r"\bsavunmaktadır\b", r"\bkanıtlamaktadır\b", r"\bgöstermektedir\b",
    r"\bbelirtmektedir\b", r"\bvurgulamaktadır\b", r"\bartmaktadır\b",
    r"\bazalmaktadır\b", r"\bdesteklemektedir\b", r"\bçürütmektedir\b",
    r"\beleştirmektedir\b", r"\bkarşı çıkmaktadır\b",
]

_CLAIM_MARKERS_EN = [
    r"\bfinds?\b", r"\bshows?\b", r"\bdemonstrates?\b", r"\bargues?\b",
    r"\bclaims?\b", r"\bsuggests?\b", r"\bcontends?\b", r"\basserts?\b",
    r"\bconcludes?\b", r"\bincreases?\b", r"\bdecreases?\b",
    r"\bsupports?\b", r"\brefutes?\b", r"\bchallenges?\b", r"\bcritiques?\b",
    r"\bcontradicts?\b", r"\bdisputes?\b",
]

_NEGATION_PATTERNS = [
    # TR
    r"\bdeğil\b", r"\baksine\b", r"\byerine\b", r"\bkarşın\b",
    r"\brağmen\b", r"\boysa\b", r"\bancak\b", r"\bfakat\b",
    r"\böte yandan\b", r"\bbuna karşın\b", r"\bbununla birlikte\b",
    # EN
    r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bcontrary\b", r"\bdespite\b",
    r"\bhowever\b", r"\byet\b", r"\balthough\b", r"\bwhereas\b",
    r"\bwhile\b", r"\bin contrast\b", r"\bon the other hand\b",
]

_ALL_CLAIM_PATTERN = re.compile(
    "|".join(_CLAIM_MARKERS_TR + _CLAIM_MARKERS_EN),
    re.IGNORECASE,
)
_NEGATION_PATTERN = re.compile(
    "|".join(_NEGATION_PATTERNS),
    re.IGNORECASE,
)

# Keyword extraction: pull noun phrases (simple heuristic)
_WORD_PATTERN = re.compile(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b")


def parse_note_file(path: Path) -> dict:
    """Bir not dosyasını parse eder: başlık, kaynak, iddialar."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Extract title (first H1 or filename)
    title = path.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract source reference (DOI, URL, or cited paper)
    source_ref = ""
    doi_match = re.search(r"10\.\d{4,9}/\S+", content)
    if doi_match:
        source_ref = doi_match.group(0).rstrip(".,;)")
    else:
        # Look for "Kaynak:", "Source:", or "DOI:" lines
        for line in lines:
            if re.match(r"^(Kaynak|Source|DOI|URL)\s*:", line, re.IGNORECASE):
                source_ref = line.split(":", 1)[1].strip()
                break

    # Extract claim sentences (sentences containing epistemic markers)
    claims = []
    # Split into sentences (simple approach)
    text = re.sub(r"\n+", " ", content)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 400:
            continue
        if _ALL_CLAIM_PATTERN.search(sent):
            claims.append(sent)

    return {
        "file": path.name,
        "title": title,
        "source_ref": source_ref,
        "claims": claims,
        "full_text": content,
    }


def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    """Metinden en sık geçen anlamlı kelimeleri çıkarır."""
    # Stop words (TR + EN basic)
    stop_words = {
        "için", "ile", "bir", "olan", "olarak", "ancak", "fakat", "this",
        "that", "with", "from", "have", "been", "their", "they", "will",
        "more", "also", "such", "these", "those", "into", "other", "which",
        "when", "where", "what", "were", "than", "then", "some", "each",
    }
    words = _WORD_PATTERN.findall(text.lower())
    freq: dict[str, int] = defaultdict(int)
    for w in words:
        if w not in stop_words and len(w) >= 4:
            freq[w] += 1
    return sorted(freq, key=lambda w: -freq[w])[:top_n]


def find_contradictions(notes: list[dict]) -> list[dict]:
    """
    Notlar arasında potansiyel çelişkileri tespit eder.

    Algoritma:
    1. Her not çiftini karşılaştır
    2. Ortak anahtar kelime paylaşan çiftleri bul (konu örtüşmesi)
    3. Karşıt ifadeler içeren iddia çiftlerini işaretle
    """
    contradictions = []
    seen_pairs: set[frozenset] = set()

    for i, note_a in enumerate(notes):
        if not note_a["claims"]:
            continue
        keywords_a = set(extract_keywords(note_a["full_text"]))

        for j, note_b in enumerate(notes):
            if i >= j:
                continue
            pair_key = frozenset([note_a["file"], note_b["file"]])
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            if not note_b["claims"]:
                continue
            keywords_b = set(extract_keywords(note_b["full_text"]))

            # Check topic overlap
            shared_keywords = keywords_a & keywords_b
            if len(shared_keywords) < 2:
                continue  # Different topics — no meaningful comparison

            # Find potentially contradicting claim pairs
            conflict_pairs = []
            for claim_a in note_a["claims"]:
                kw_a = set(extract_keywords(claim_a, top_n=5))
                for claim_b in note_b["claims"]:
                    kw_b = set(extract_keywords(claim_b, top_n=5))
                    # Claims share keywords but one has negation
                    shared_claim_kw = kw_a & kw_b
                    if len(shared_claim_kw) < 2:
                        continue
                    a_negated = bool(_NEGATION_PATTERN.search(claim_a))
                    b_negated = bool(_NEGATION_PATTERN.search(claim_b))
                    # Asymmetric negation = potential contradiction
                    if a_negated != b_negated:
                        conflict_pairs.append((claim_a, claim_b))
                    elif len(shared_claim_kw) >= 3:
                        # Even without explicit negation, closely related claims
                        # on same topic from different sources warrant review
                        conflict_pairs.append((claim_a, claim_b))

            if conflict_pairs:
                contradictions.append({
                    "source_a": note_a,
                    "source_b": note_b,
                    "shared_keywords": sorted(shared_keywords),
                    "conflict_pairs": conflict_pairs[:3],  # max 3 per pair
                })

    return contradictions


def write_report(
    project_dir: Path,
    contradictions: list[dict],
    notes: list[dict],
    output_path: Path,
) -> None:
    """CONTRADICTIONS.md raporunu yazar."""
    lines = [
        "# Çapraz Kaynak Çelişki Raporu / Cross-Source Contradiction Report",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {len(notes)} not dosyası tarandı_",
        "",
        "> **Claude için not:** Bu rapor otomatik olarak üretilmiştir.",
        "> Her çelişki adayını bağlam içinde değerlendir:",
        "> - Yazarlar farklı bağlamları mı ele alıyor? (metodoloji, popülasyon, dönem)",
        "> - Kavramsal farklılık mı var? (tanım uyuşmazlığı)",
        "> - Gerçek ampirik çelişki mi?",
        "> - Argümanını desteklemek için kullanılabilir mi?",
        "",
        "---",
        "",
    ]

    if not contradictions:
        lines += [
            "## Sonuç",
            "",
            "✅ Tarama tamamlandı. Belirgin çelişki adayı tespit edilmedi.",
            "",
            "Bu şu anlama gelebilir:",
            "- Kaynaklarınız büyük ölçüde uyumlu görüşler içeriyor",
            "- Not dosyaları henüz yeterli iddia cümlesi içermiyor",
            "- Daha fazla kaynak okundukça bu rapor güncellenmeli",
        ]
    else:
        lines += [
            f"## Tespit Edilen Çelişki Adayları: {len(contradictions)}",
            "",
            "Önem derecesine göre inceleme için sırala. "
            "Gerçek çelişkiler tezinin güçlü tartışma noktaları olabilir.",
            "",
        ]

        for i, c in enumerate(contradictions, 1):
            note_a = c["source_a"]
            note_b = c["source_b"]
            lines += [
                "---",
                "",
                f"### Çelişki {i}: {note_a['title']} ↔ {note_b['title']}",
                "",
                f"**Kaynak A:** `{note_a['file']}`"
                + (f" — {note_a['source_ref']}" if note_a["source_ref"] else ""),
                f"**Kaynak B:** `{note_b['file']}`"
                + (f" — {note_b['source_ref']}" if note_b["source_ref"] else ""),
                "",
                f"**Ortak konu:** {', '.join(c['shared_keywords'][:5])}",
                "",
                "**Çelişen İfadeler:**",
                "",
            ]
            for k, (claim_a, claim_b) in enumerate(c["conflict_pairs"], 1):
                lines += [
                    f"_{k}._ **A iddiası:**",
                    f"> {claim_a}",
                    "",
                    "   **B iddiası:**",
                    f"> {claim_b}",
                    "",
                ]
            lines += [
                "**Claude için değerlendirme soruları:**",
                "- Bu iki kaynak gerçekten çelişiyor mu, yoksa farklı boyutları mı ele alıyor?",
                "- Bu çelişki tezin hangi argümanını destekler/zayıflatır?",
                "- Bu çelişkiyi ARGUMENTS.md'e eklemeli misin?",
                "",
            ]

    # Summary table
    lines += [
        "---",
        "",
        "## Taranan Notlar",
        "",
        "| Not Dosyası | Kaynak | İddia Sayısı |",
        "|-------------|--------|--------------|",
    ]
    for n in notes:
        lines.append(
            f"| `{n['file']}` | {n['source_ref'] or '—'} | {len(n['claims'])} |"
        )

    lines += [
        "",
        "## Sonraki Adımlar",
        "",
        "1. Yukarıdaki çelişki adaylarını Claude ile incele: `/devil-advocate`",
        "2. Gerçek çelişkileri ARGUMENTS.md'e ekle",
        "3. Yeni kaynaklar okundukça tekrar çalıştır:",
        "   `python3 scripts/contradiction_scan.py`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Çapraz Kaynak Çelişki Tarayıcısı"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dosyaları dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="CONTRADICTIONS.md",
        help="Çıktı rapor dosyası (varsayılan: CONTRADICTIONS.md)",
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
        print(f"⚠️  Not dizini bulunamadı: {notes_dir}")
        print("💡 Önce kaynakları oku ve notlarını notes/ klasörüne kaydet.")
        sys.exit(0)

    note_files = sorted(notes_dir.glob("*.md"))
    if not note_files:
        print("ℹ️  notes/ dizininde hiç .md dosyası yok.")
        print("💡 Her kaynak için bir not dosyası oluştur ve tekrar çalıştır.")
        sys.exit(0)

    print(f"📝 {len(note_files)} not dosyası taranıyor...")

    notes = []
    for path in note_files:
        note = parse_note_file(path)
        notes.append(note)
        claim_count = len(note["claims"])
        print(f"   • {path.name}: {claim_count} iddia cümlesi")

    # Also scan ARGUMENTS.md and SYNTHESIS.md for additional claims
    for extra_file in ["ARGUMENTS.md", "SYNTHESIS.md"]:
        extra_path = project_dir / extra_file
        if extra_path.exists():
            extra_note = parse_note_file(extra_path)
            if extra_note["claims"]:
                notes.append(extra_note)
                print(f"   • {extra_file}: {len(extra_note['claims'])} iddia cümlesi (ek tarama)")

    print()
    print("🔍 Çelişki taraması yapılıyor...")
    contradictions = find_contradictions(notes)

    write_report(project_dir, contradictions, notes, output_path)

    print()
    print(f"{'─' * 50}")
    print(f"  Taranan not sayısı  : {len(notes)}")
    print(f"  Çelişki adayı       : {len(contradictions)}")
    print(f"  Rapor               : {output_path.name}")
    print(f"{'─' * 50}")
    print()

    if contradictions:
        print(f"⚠️  {len(contradictions)} çelişki adayı tespit edildi.")
        print("📋 CONTRADICTIONS.md dosyasını Claude ile incele:")
        print("   Read tool ile dosyayı aç ve `/devil-advocate` komutunu kullan.")
    else:
        print("✅ Belirgin çelişki tespit edilmedi.")
        print("💡 Daha fazla kaynak okuyup notlarını ekledikçe tekrar çalıştır.")


if __name__ == "__main__":
    main()
