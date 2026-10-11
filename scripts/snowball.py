#!/usr/bin/env python3
"""
scripts/snowball.py — TezAtlas Kartopu Örnekleme Otomasyonu
                     Snowball Sampling Automation

OCR çıktısından veya sources/ PDF'lerinden referans DOI/başlıklarını çıkarır,
READING_REPORT.md'deki mevcut kaynaklarla karşılaştırır ve yeni adayları önerir.

Kullanım:
    python3 scripts/snowball.py --from-notes notes/        # notlardan DOI çıkar
    python3 scripts/snowball.py --from-pdf sources/paper.pdf  # tek PDF'den
    python3 scripts/snowball.py --from-dir sources/        # tüm sources/ klasöründen
    python3 scripts/snowball.py --add                      # yeni adayları okuma havuzuna ekle

Çıktı: SNOWBALL_CANDIDATES.md — inceleme için aday kaynaklar listesi
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from datetime import date

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

# ── DOI pattern ──────────────────────────────────────────────────────────────

# Matches DOIs like 10.1234/something or 10.1234/something.more
_DOI_PATTERN = re.compile(
    r"\b(10\.\d{4,9}/[^\s\"'<>,;)(}{|\[\]]+)",
    re.IGNORECASE,
)

# Reference line patterns (bibliography entries)
_REF_PATTERNS = [
    # APA: Author, A. (Year). Title...
    re.compile(r"^\s*\[?\d+\]?\s+[A-Z][a-z]+,\s+[A-Z]"),
    # Numbered: [1] or 1.
    re.compile(r"^\s*\[\d+\]\s+\S"),
    re.compile(r"^\s*\d+\.\s+[A-Z]"),
]


def extract_dois_from_text(text: str) -> list[str]:
    """Ham metinden tüm DOI'leri çıkarır."""
    dois = _DOI_PATTERN.findall(text)
    # Clean trailing punctuation that got captured
    cleaned = []
    for doi in dois:
        doi = doi.rstrip(".,;)")
        if doi not in cleaned:
            cleaned.append(doi)
    return cleaned


def extract_dois_from_pdf(pdf_path: Path) -> list[str]:
    """PyMuPDF ile PDF'den DOI çıkarır."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[UYARI] PyMuPDF yüklü değil. pip install pymupdf", file=sys.stderr)
        return []

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"[HATA] PDF açılamadı {pdf_path}: {e}", file=sys.stderr)
        return []

    all_dois: list[str] = []
    # Focus on last 20% of pages (bibliography usually at end)
    total = len(doc)
    start_page = max(0, int(total * 0.7))

    for page_num in range(start_page, total):
        text = doc[page_num].get_text()
        dois = extract_dois_from_text(text)
        all_dois.extend(dois)

    # Also scan full document for inline citations
    for page_num in range(min(start_page, total)):
        text = doc[page_num].get_text()
        dois = extract_dois_from_text(text)
        all_dois.extend(dois)

    doc.close()
    return list(dict.fromkeys(all_dois))  # deduplicate, preserve order


def extract_dois_from_notes(notes_dir: Path) -> dict[str, list[str]]:
    """notes/*.md dosyalarından DOI çıkarır. {dosya: [doi, ...]} döner."""
    result: dict[str, list[str]] = {}
    if not notes_dir.is_dir():
        return result
    for note_file in sorted(notes_dir.glob("*.md")):
        text = note_file.read_text(encoding="utf-8")
        dois = extract_dois_from_text(text)
        if dois:
            result[note_file.name] = dois
    return result


def load_existing_dois(project_dir: Path) -> set[str]:
    """READING_REPORT.md'deki mevcut DOI'leri yükler."""
    report_path = project_dir / "READING_REPORT.md"
    if not report_path.exists():
        return set()
    content = report_path.read_text(encoding="utf-8")
    return set(extract_dois_from_text(content))


def load_candidates(project_dir: Path) -> list[dict]:
    """Mevcut SNOWBALL_CANDIDATES.md'i parse eder."""
    path = project_dir / "SNOWBALL_CANDIDATES.md"
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    candidates = []
    for line in content.splitlines():
        if line.strip().startswith("|") and "---" not in line and "DOI" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[1]:  # DOI column
                candidates.append({
                    "doi": parts[1],
                    "source_file": parts[2] if len(parts) > 2 else "",
                    "status": parts[3] if len(parts) > 3 else "🔵 Aday",
                })
    return candidates


def write_candidates_report(
    project_dir: Path,
    new_dois: list[tuple[str, str]],  # (doi, source_file)
    existing_dois: set[str],
    existing_candidates: list[dict],
) -> int:
    """SNOWBALL_CANDIDATES.md dosyasını yazar/günceller. Kaç yeni eklendi döner."""
    path = project_dir / "SNOWBALL_CANDIDATES.md"

    # Collect all known DOIs (already in report or existing candidates)
    known_dois = set(existing_dois)
    for c in existing_candidates:
        known_dois.add(c["doi"])

    # Filter truly new
    added = []
    for doi, source_file in new_dois:
        if doi not in known_dois:
            added.append({"doi": doi, "source_file": source_file, "status": "🔵 Aday"})
            known_dois.add(doi)

    if not added and not existing_candidates:
        return 0

    all_candidates = existing_candidates + added

    lines = [
        "# Kartopu Örnekleme Adayları / Snowball Sampling Candidates",
        "",
        f"_Son güncelleme: {date.today().isoformat()}_",
        "",
        "Bu liste, mevcut kaynaklardan otomatik çıkarılan referans DOI'lerini içerir.",
        "🔵 Aday = henüz incelenmedi | ✅ Eklendi = okuma havuzuna alındı | ❌ Dışlandı = kapsam dışı",
        "",
        "| # | DOI | Kaynak Dosya | Durum |",
        "|---|-----|--------------|-------|",
    ]
    for i, c in enumerate(all_candidates, 1):
        lines.append(f"| {i} | {c['doi']} | {c['source_file']} | {c['status']} |")

    lines += [
        "",
        "## Sonraki Adımlar",
        "",
        "1. DOI linklerini kontrol et: `https://doi.org/<DOI>`",
        "2. İlgili olanları okuma havuzuna ekle:",
        "   ```",
        "   python3 scripts/find_source.py --doi '10.xxxx/xxxxx'",
        "   python3 scripts/reading_tracker.py sync",
        "   ```",
        "3. Kapsam dışı olanları ❌ Dışlandı olarak işaretle (bu dosyayı düzenle)",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return len(added)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas Kartopu Örnekleme — Otomatik DOI Çıkarıcı"
    )
    parser.add_argument(
        "--from-notes", metavar="DIR",
        help="notes/ dizininden DOI çıkar (varsayılan: ./notes/)",
    )
    parser.add_argument(
        "--from-pdf", metavar="PDF",
        help="Tek bir PDF'den DOI çıkar",
    )
    parser.add_argument(
        "--from-dir", metavar="DIR",
        help="sources/ gibi bir dizindeki tüm PDF'lerden DOI çıkar",
    )
    parser.add_argument(
        "--project-dir", metavar="DIR", default=".",
        help="Proje kök dizini (varsayılan: .)",
    )
    parser.add_argument(
        "--add", action="store_true",
        help="SNOWBALL_CANDIDATES.md'deki tüm 🔵 Aday DOI'leri find_source.py ile indir",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    # ── Collect DOIs ──────────────────────────────────────────────────────────
    new_dois: list[tuple[str, str]] = []  # (doi, source_label)

    if args.from_pdf:
        pdf_path = Path(args.from_pdf)
        print(f"📄 PDF taranıyor: {pdf_path.name}")
        dois = extract_dois_from_pdf(pdf_path)
        for d in dois:
            new_dois.append((d, pdf_path.name))

    if args.from_dir:
        src_dir = Path(args.from_dir)
        pdfs = list(src_dir.glob("*.pdf"))
        print(f"📁 {len(pdfs)} PDF taranıyor: {src_dir}/")
        for pdf in pdfs:
            dois = extract_dois_from_pdf(pdf)
            for d in dois:
                new_dois.append((d, pdf.name))

    notes_dir = Path(args.from_notes) if args.from_notes else project_dir / "notes"
    if notes_dir.is_dir():
        note_dois = extract_dois_from_notes(notes_dir)
        if note_dois:
            for fname, dois in note_dois.items():
                for d in dois:
                    new_dois.append((d, fname))
            total_note_dois = sum(len(v) for v in note_dois.values())
            print(f"📝 {len(note_dois)} not dosyasından {total_note_dois} DOI çıkarıldı")

    # ── Load existing state ───────────────────────────────────────────────────
    existing_dois = load_existing_dois(project_dir)
    existing_candidates = load_candidates(project_dir)

    # ── Handle --add flag ─────────────────────────────────────────────────────
    if args.add:
        if not existing_candidates:
            print("ℹ️  SNOWBALL_CANDIDATES.md boş ya da bulunamadı.")
            return
        candidates_to_add = [c for c in existing_candidates if c["status"] == "🔵 Aday"]
        if not candidates_to_add:
            print("ℹ️  Eklenecek yeni aday yok.")
            return
        print(f"\n🔗 {len(candidates_to_add)} aday DOI find_source.py ile aranacak:\n")
        for c in candidates_to_add:
            print(f"  • {c['doi']}")
        print()
        import subprocess
        for c in candidates_to_add:
            doi = c["doi"]
            print(f"⏳ İndiriliyor: {doi}")
            result = subprocess.run(
                [sys.executable, "scripts/find_source.py", "--doi", doi,
                 "--output", str(project_dir / "sources")],
                cwd=str(project_dir),
            )
            if result.returncode == 0:
                c["status"] = "✅ Eklendi"
            else:
                print(f"  ⚠️  İndirilemedi: {doi}")
        # Rewrite with updated statuses
        path = project_dir / "SNOWBALL_CANDIDATES.md"
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        for c in candidates_to_add:
            if c["status"] == "✅ Eklendi":
                content = content.replace(
                    f"| {c['doi']} |",
                    f"| {c['doi']} |",  # status column update needs full rewrite
                )
        write_candidates_report(project_dir, [], existing_dois, existing_candidates)
        print("\n✅ SNOWBALL_CANDIDATES.md güncellendi.")
        print("💡 Sonraki adım: python3 scripts/reading_tracker.py sync")
        return

    # ── Write/update report ───────────────────────────────────────────────────
    if not new_dois:
        print("ℹ️  Hiç DOI bulunamadı.")
        print("💡 Not dosyalarına veya PDF'lere DOI içeren referanslar eklendiğinde tekrar çalıştır.")
        return

    added_count = write_candidates_report(
        project_dir, new_dois, existing_dois, existing_candidates
    )

    total_found = len(new_dois)
    already_known = total_found - added_count

    print("\n🔍 Kartopu Örnekleme Sonuçları")
    print(f"{'─' * 40}")
    print(f"  Taranan DOI toplamı : {total_found}")
    print(f"  Zaten bilinen        : {already_known}")
    print(f"  Yeni aday            : {added_count}")
    print()

    if added_count > 0:
        print(f"✅ {added_count} yeni aday SNOWBALL_CANDIDATES.md'e eklendi.")
        print()
        print("Sonraki adımlar:")
        print("  1. SNOWBALL_CANDIDATES.md dosyasını incele")
        print("  2. İlgili DOI'leri indir:")
        print("     python3 scripts/snowball.py --add")
        print("  3. İndirdikten sonra okuma takipçisini güncelle:")
        print("     python3 scripts/reading_tracker.py sync")
    else:
        print("ℹ️  Tüm bulunan DOI'ler zaten okuma havuzunda.")


if __name__ == "__main__":
    main()
