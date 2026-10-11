#!/usr/bin/env python3
"""
scripts/intake_protocol.py — TezAtlas Kaynak Haritası Protokolü
                              Source Intake Protocol

notes/*.md dosyalarını tarar, her kaynağı özetler, paylaşılan varsayımlara göre
kümeler ve çelişen kaynakları işaretler.

Kullanım:
    python3 scripts/intake_protocol.py                  # varsayılan: ./notes/
    python3 scripts/intake_protocol.py --notes notes/
    python3 scripts/intake_protocol.py --output SOURCE_MAP.md

Çıktı: SOURCE_MAP.md — kümelenmiş kaynak haritası
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

_NEGATION_PATTERNS = re.compile(
    r"\b(değil|aksine|yerine|karşın|rağmen|oysa|ancak|fakat|öte yandan|"
    r"not|no|never|contrary|despite|however|yet|although|whereas|in contrast)\b",
    re.IGNORECASE,
)

_CLAIM_PATTERN = re.compile(
    r"\b(bulgu|sonuç|iddia|öne sürmektedir|savunmaktadır|kanıtlamaktadır|"
    r"göstermektedir|belirtmektedir|vurgulamaktadır|desteklemektedir|"
    r"finds?|shows?|demonstrates?|argues?|claims?|suggests?|concludes?|"
    r"supports?|refutes?|challenges?|contends?|asserts?)\b",
    re.IGNORECASE,
)


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Metinden en sık geçen anlamlı kelimeleri çıkarır."""
    words = _WORD_PATTERN.findall(text.lower())
    freq: dict[str, int] = defaultdict(int)
    for w in words:
        if w not in _STOP_WORDS:
            freq[w] += 1
    return sorted(freq, key=lambda w: -freq[w])[:top_n]


# ── Note parsing ──────────────────────────────────────────────────────────────

def parse_note(path: Path) -> dict:
    """Bir not dosyasını parse eder: başlık, yazar, yıl, temel iddia, anahtar kelimeler."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Title
    title = path.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Author extraction (look for author-like patterns)
    author = ""
    for line in lines:
        m = re.match(r"^(?:Yazar|Author|Yazarlar|Authors)\s*:\s*(.+)", line, re.IGNORECASE)
        if m:
            author = m.group(1).strip()
            break
    if not author:
        # Try to extract from title format: "Author (Year) - Title"
        m = re.match(r"^([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+(?:ve|and|&)\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)", title)
        if m:
            author = m.group(1)

    # Year extraction
    year = ""
    year_match = re.search(r"\b(19[89]\d|20[0-2]\d)\b", content[:500])
    if year_match:
        year = year_match.group(1)

    # DOI
    doi = ""
    doi_match = re.search(r"10\.\d{4,9}/\S+", content)
    if doi_match:
        doi = doi_match.group(0).rstrip(".,;)")

    # Core claim — first sentence with an epistemic marker
    core_claim = ""
    text_flat = re.sub(r"\n+", " ", content)
    sentences = re.split(r"(?<=[.!?])\s+", text_flat)
    for sent in sentences:
        sent = sent.strip()
        if 20 < len(sent) < 300 and _CLAIM_PATTERN.search(sent):
            core_claim = sent
            break

    # All claims
    claims = []
    for sent in sentences:
        sent = sent.strip()
        if 20 < len(sent) < 400 and _CLAIM_PATTERN.search(sent):
            claims.append(sent)

    keywords = extract_keywords(content)

    return {
        "file": path.name,
        "title": title,
        "author": author,
        "year": year,
        "doi": doi,
        "core_claim": core_claim,
        "claims": claims,
        "keywords": keywords,
        "content": content,
    }


# ── Clustering ────────────────────────────────────────────────────────────────

def cluster_by_keywords(notes: list[dict]) -> list[dict]:
    """Notları paylaşılan anahtar kelimelere göre kümeler."""
    if not notes:
        return []

    # Build keyword → notes mapping
    keyword_notes: dict[str, list[int]] = defaultdict(list)
    for i, note in enumerate(notes):
        for kw in note["keywords"][:8]:
            keyword_notes[kw].append(i)

    # Find keyword groups that connect multiple notes
    # Use a simple greedy approach: pick most shared keywords as cluster centers
    used = set()
    clusters = []

    # Sort keywords by how many notes they connect
    sorted_kws = sorted(keyword_notes.items(), key=lambda x: -len(x[1]))

    for kw, note_indices in sorted_kws:
        # Only consider keywords shared by 2+ notes
        remaining = [i for i in note_indices if i not in used]
        if len(remaining) < 2:
            continue

        # Find all shared keywords among these notes
        cluster_kws = set()
        for i in remaining:
            for j in remaining:
                if i >= j:
                    continue
                shared = set(notes[i]["keywords"][:8]) & set(notes[j]["keywords"][:8])
                cluster_kws |= shared

        cluster_notes = remaining
        for i in cluster_notes:
            used.add(i)

        clusters.append({
            "shared_keywords": sorted(cluster_kws)[:5],
            "note_indices": cluster_notes,
        })

    # Add unclustered notes
    unclustered = [i for i in range(len(notes)) if i not in used]
    if unclustered:
        clusters.append({
            "shared_keywords": ["(bağımsız / independent)"],
            "note_indices": unclustered,
        })

    return clusters


# ── Contradiction detection (lightweight) ─────────────────────────────────────

def detect_conflicts(notes: list[dict]) -> list[dict]:
    """Kümeler arası çelişen kaynak çiftlerini tespit eder."""
    conflicts = []
    seen = set()

    for i, note_a in enumerate(notes):
        if not note_a["claims"]:
            continue
        kw_a = set(note_a["keywords"][:8])

        for j, note_b in enumerate(notes):
            if i >= j:
                continue
            pair = frozenset([i, j])
            if pair in seen:
                continue

            if not note_b["claims"]:
                continue
            kw_b = set(note_b["keywords"][:8])

            shared = kw_a & kw_b
            if len(shared) < 2:
                continue

            # Check for asymmetric negation in related claims
            for ca in note_a["claims"][:5]:
                for cb in note_b["claims"][:5]:
                    ca_kw = set(extract_keywords(ca, 5))
                    cb_kw = set(extract_keywords(cb, 5))
                    if len(ca_kw & cb_kw) < 2:
                        continue
                    a_neg = bool(_NEGATION_PATTERNS.search(ca))
                    b_neg = bool(_NEGATION_PATTERNS.search(cb))
                    if a_neg != b_neg:
                        seen.add(pair)
                        conflicts.append({
                            "note_a": note_a["file"],
                            "note_b": note_b["file"],
                            "claim_a": ca,
                            "claim_b": cb,
                            "shared": sorted(shared),
                        })
                        break
                else:
                    continue
                break

    return conflicts


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(
    notes: list[dict],
    clusters: list[dict],
    conflicts: list[dict],
    output_path: Path,
) -> None:
    """SOURCE_MAP.md raporunu yazar."""
    lines = [
        "# Kaynak Haritası / Source Intake Map",
        "",
        f"_Oluşturulma: {date.today().isoformat()} — {len(notes)} kaynak tarandı_",
        "",
        "> Bu rapor, kaynaklarınızı otomatik olarak kümeleyip çelişkileri işaretler.",
        "> Her kaynağın temel iddiasını ve kümeler arası ilişkileri gösterir.",
        "",
        "---",
        "",
    ]

    # ── Source summary table ──
    lines += [
        "## Kaynak Özeti / Source Summary",
        "",
        "| # | Dosya | Yazar | Yıl | Temel İddia |",
        "|---|-------|-------|-----|-------------|",
    ]
    for i, n in enumerate(notes, 1):
        claim_short = n["core_claim"][:80] + "..." if len(n["core_claim"]) > 80 else n["core_claim"]
        if not claim_short:
            claim_short = "_(iddia çıkarılamadı)_"
        lines.append(
            f"| {i} | `{n['file']}` | {n['author'] or '—'} | {n['year'] or '—'} | {claim_short} |"
        )
    lines += ["", "---", ""]

    # ── Clusters ──
    lines += [
        "## Kümeleme / Clusters",
        "",
        "Paylaşılan varsayım ve kavramlara göre gruplandırılmış kaynaklar:",
        "",
    ]
    for ci, cluster in enumerate(clusters, 1):
        kw_str = ", ".join(cluster["shared_keywords"][:5])
        lines += [
            f"### Küme {ci}: {kw_str}",
            "",
        ]
        for idx in cluster["note_indices"]:
            n = notes[idx]
            claim = n["core_claim"][:100] if n["core_claim"] else "—"
            lines.append(f"- **{n['title']}** (`{n['file']}`) — {claim}")
        lines += [""]

    # ── Conflicts ──
    lines += [
        "---",
        "",
        f"## Çelişen Kaynaklar / Conflicting Sources ({len(conflicts)})",
        "",
    ]
    if conflicts:
        lines.append("Aşağıdaki kaynak çiftleri aynı konuda farklı iddialarda bulunuyor:")
        lines.append("")
        for ci, c in enumerate(conflicts, 1):
            lines += [
                f"### ⚠️ Çelişki {ci}: `{c['note_a']}` ↔ `{c['note_b']}`",
                "",
                f"**Ortak konu:** {', '.join(c['shared'][:4])}",
                "",
                "**A iddiası:**",
                f"> {c['claim_a']}",
                "",
                "**B iddiası:**",
                f"> {c['claim_b']}",
                "",
            ]
    else:
        lines += [
            "✅ Belirgin çelişki tespit edilmedi.",
            "",
            "Daha fazla kaynak ekledikçe bu raporu güncelle:",
            "`python3 scripts/intake_protocol.py`",
            "",
        ]

    # ── Next steps ──
    lines += [
        "---",
        "",
        "## Sonraki Adımlar",
        "",
        "1. Kümeleri incele — eksik perspektif var mı?",
        "2. Çelişkileri `/devil-advocate` ile tartış",
        "3. Boşlukları `/gaps` ile tara",
        "4. Yeni kaynak ekledikçe güncelle: `python3 scripts/intake_protocol.py`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Kaynak Haritası Protokolü"
    )
    parser.add_argument(
        "--notes", metavar="DIR", default="notes",
        help="Not dizini (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--output", metavar="FILE", default="SOURCE_MAP.md",
        help="Çıktı dosyası (varsayılan: SOURCE_MAP.md)",
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
        print(f"   • {path.name}: {note['author'] or '?'} ({note['year'] or '?'}) — {len(note['claims'])} iddia")

    print("\n🔗 Kümeleme yapılıyor...")
    clusters = cluster_by_keywords(notes)
    print(f"   {len(clusters)} küme oluşturuldu")

    print("🔍 Çelişki taraması...")
    conflicts = detect_conflicts(notes)

    write_report(notes, clusters, conflicts, output_path)

    print()
    print(f"{'─' * 50}")
    print(f"  Taranan kaynak      : {len(notes)}")
    print(f"  Küme sayısı         : {len(clusters)}")
    print(f"  Çelişki adayı       : {len(conflicts)}")
    print(f"  Rapor               : {output_path.name}")
    print(f"{'─' * 50}")

    if conflicts:
        print(f"\n⚠️  {len(conflicts)} çelişki adayı tespit edildi.")
    else:
        print("\n✅ Belirgin çelişki tespit edilmedi.")


if __name__ == "__main__":
    main()
