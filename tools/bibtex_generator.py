#!/usr/bin/env python3
"""
TezAtlas BibTeX/RIS Generator
-------------------------------
Extracts DOIs from PDFs and fetches structured bibliographic metadata
from CrossRef API. Fallback: title/author heuristic + OpenAlex/Semantic Scholar.

Usage:
    python3 tools/bibtex_generator.py sources/paper.pdf
    python3 tools/bibtex_generator.py sources/              # batch — all PDFs
    python3 tools/bibtex_generator.py sources/ --format ris # RIS instead of BibTeX
    python3 tools/bibtex_generator.py sources/ --output refs/references.bib

Outputs:
    - Single file: <filename>.bib (or .ris) next to the PDF by default
    - Batch: combined references.bib in project root (or --output path)
"""

import os
import argparse
import unicodedata
from difflib import SequenceMatcher
import json
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# ── DOI regex ────────────────────────────────────────────────────────────────
# Matches DOIs like: 10.1234/something, 10.1234/something.v2
DOI_PATTERN = re.compile(
    r"\b(10\.\d{4,9}/[^\s\"'<>,;:)(}{]+)",
    re.IGNORECASE,
)

CROSSREF_API = "https://api.crossref.org/works/"
OPENALEX_API = "https://api.openalex.org/works"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

# Polite pool: identify ourselves to CrossRef
# Crossref/OpenAlex "polite pool" için iletişim adresi (.env: TEZATLAS_MAILTO)
MAILTO = os.environ.get("TEZATLAS_MAILTO", "tezatlas@example.com")


# ── PDF text extraction ───────────────────────────────────────────────────────

def extract_first_pages(pdf_path: str, max_pages: int = 3) -> str:
    """Extract text from the first N pages of a PDF."""
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf")
    doc = fitz.open(pdf_path)
    pages_text = []
    for i in range(min(max_pages, len(doc))):
        pages_text.append(doc[i].get_text())
    doc.close()
    return "\n".join(pages_text)


def find_dois(text: str) -> list[str]:
    """Find all DOI strings in text. Returns unique DOIs, most likely first."""
    raw = DOI_PATTERN.findall(text)
    # Clean trailing punctuation artifacts
    cleaned = [doi.rstrip(".,;)]}") for doi in raw]
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for doi in cleaned:
        if doi.lower() not in seen:
            seen.add(doi.lower())
            unique.append(doi)
    return unique


# ── Doğrulama ve kaçışlama yardımcıları ───────────────────────────────────────

def _norm(text: str) -> str:
    """Karşılaştırma için: küçük harf, aksan ve noktalama yok, tek boşluk."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("ı", "i").casefold()
    text = re.sub(r"<[^>]+>", " ", text)          # Crossref başlıklarındaki <i>, <sub> vb.
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_matches_text(title: str, text: str, threshold: float = 0.85) -> bool:
    """Bir künye başlığının PDF'in ilk sayfalarında gerçekten geçip geçmediğini denetler.

    PDF'in ilk sayfalarında başka eserlerin DOI'leri (atıf satırı, kaynakça) sık bulunur.
    Bu yüzden DOI'den gelen künye, başlığı PDF metninde bulunmadıkça kabul edilmez.
    """
    t = _norm(title)
    if not t:
        return False
    body = _norm(text)
    if t in body:
        return True
    words = t.split()
    if len(words) < 3:
        return False
    # Satır kırılmaları ve tirelemeye karşı: başlık uzunluğundaki pencerelerde benzerlik
    body_words = body.split()
    n = len(words)
    best = 0.0
    for i in range(0, max(1, len(body_words) - n + 1)):
        window = " ".join(body_words[i:i + n])
        ratio = SequenceMatcher(None, t, window).ratio()
        if ratio > best:
            best = ratio
            if best >= threshold:
                return True
    return False


_LATEX_SPECIAL = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_"}


def bib_escape(value: str) -> str:
    """BibTeX alan değerinde LaTeX özel karakterlerini kaçışlar (zaten kaçışlıysa dokunmaz)."""
    value = re.sub(r"<[^>]+>", "", str(value or ""))
    return re.sub(r"(?<!\\)([&%$#_])", lambda m: _LATEX_SPECIAL[m.group(1)], value)


def ascii_key(text: str) -> str:
    """Atıf anahtarı için ASCII'ye indirger: 'Öz' → 'Oz', 'Çağlar' → 'Caglar'."""
    text = unicodedata.normalize("NFKD", (text or "").replace("ı", "i").replace("İ", "I"))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]", "", text) or "Unknown"


def make_keys_unique(entries: list[str]) -> list[str]:
    """Aynı yazar-yıl anahtarlarına a, b, c… son eki ekler."""
    seen: dict[str, int] = {}
    out = []
    for entry in entries:
        m = re.match(r"(@\w+\{)([^,]+),", entry)
        if not m:
            out.append(entry)
            continue
        key = m.group(2)
        count = seen.get(key, 0)
        seen[key] = count + 1
        if count:
            entry = entry.replace(m.group(0), f"{m.group(1)}{key}{chr(ord('a') + count - 1)},", 1)
        out.append(entry)
    return out


# ── CrossRef API ──────────────────────────────────────────────────────────────

def fetch_crossref(doi: str) -> dict | None:
    """Fetch metadata from CrossRef API for a given DOI."""
    url = CROSSREF_API + urllib.parse.quote(doi, safe="") + f"?mailto={MAILTO}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"TezAtlas/1.0 (mailto:{MAILTO})"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("message", {})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # DOI not found in CrossRef
        raise
    except Exception:
        return None


# ── OpenAlex API (title fallback) ─────────────────────────────────────────────

def search_openalex(title: str, author: str = "") -> dict | None:
    """Search OpenAlex by title for bibliographic metadata."""
    query = title[:120]  # API limit
    params = urllib.parse.urlencode({
        "search": query,
        "per-page": "1",
        "mailto": MAILTO,
    })
    url = f"{OPENALEX_API}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TezAtlas/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            return results[0] if results else None
    except Exception:
        return None


def search_openalex_many(title: str, limit: int = 5) -> list[dict]:
    """OpenAlex'te başlıkla arar ve ilk birkaç sonucu döndürür (doğrulama çağıran tarafta)."""
    params = urllib.parse.urlencode({"search": title[:120], "per-page": str(limit), "mailto": MAILTO})
    try:
        req = urllib.request.Request(f"{OPENALEX_API}?{params}", headers={"User-Agent": f"TezAtlas/1.1 (mailto:{MAILTO})"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()).get("results", []) or []
    except Exception:
        return []


# ── Heuristic title/author extraction ─────────────────────────────────────────

def extract_title_author(text: str) -> tuple[str, str]:
    """
    Heuristic: extract title and first author from PDF first page text.
    Assumes: title is on one of the first 3 non-empty lines,
             author follows shortly after.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = ""
    author = ""

    # Title: first substantial line (>20 chars, not a header/page number)
    for line in lines[:15]:
        if len(line) > 20 and not line.startswith(("doi:", "DOI:", "http", "www", "©", "Abstract")):
            title = line
            break

    # Author: look for a line that looks like "Firstname Lastname" in first 20 lines
    author_pattern = re.compile(r"^[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+ [A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+")
    for line in lines[1:20]:
        if author_pattern.match(line) and len(line) < 80:
            author = line
            break

    return title, author


# ── BibTeX generation ─────────────────────────────────────────────────────────

def crossref_to_bibtex(doi: str, data: dict) -> str:
    """Convert CrossRef API response to BibTeX entry."""
    entry_type = {
        "journal-article": "article",
        "book": "book",
        "book-chapter": "incollection",
        "proceedings-article": "inproceedings",
        "report": "techreport",
        "dissertation": "phdthesis",
        "posted-content": "misc",
    }.get(data.get("type", ""), "misc")

    # Key: first author last name + year
    authors = data.get("author", [])
    first_author = authors[0].get("family", "Unknown") if authors else "Unknown"
    year_info = data.get("published", data.get("published-print", {}))
    year = str(year_info.get("date-parts", [[""]])[0][0]) if year_info else ""
    key = f"{ascii_key(first_author)}{year}"

    # Author list
    author_str = bib_escape(" and ".join(
        f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
        for a in authors
    ))

    # Title
    title_list = data.get("title", [""])
    title = bib_escape(title_list[0] if title_list else "")

    # Journal/container
    container = data.get("container-title", [""])
    journal = bib_escape(container[0] if container else "")

    volume = data.get("volume", "")
    issue = data.get("issue", "")
    pages = data.get("page", "")
    publisher = bib_escape(data.get("publisher", ""))
    url = f"https://doi.org/{doi}"

    lines = [f"@{entry_type}{{{key},"]
    if author_str:
        lines.append(f"  author = {{{author_str}}},")
    if title:
        lines.append(f"  title = {{{{{title}}}}},")
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if volume:
        lines.append(f"  volume = {{{volume}}},")
    if issue:
        lines.append(f"  number = {{{issue}}},")
    if pages:
        lines.append(f"  pages = {{{pages}}},")
    if publisher:
        lines.append(f"  publisher = {{{publisher}}},")
    lines.append(f"  doi = {{{doi}}},")
    lines.append(f"  url = {{{url}}},")
    lines.append("}")

    return "\n".join(lines)


def openalex_to_bibtex(work: dict) -> str:
    """Convert OpenAlex work object to BibTeX entry."""
    title = bib_escape(work.get("title") or "Unknown")
    year = work.get("publication_year", "")
    doi = (work.get("doi") or "").replace("https://doi.org/", "")

    authors = work.get("authorships", [])
    author_parts = []
    for a in authors[:6]:  # cap at 6 authors
        display = a.get("author", {}).get("display_name", "")
        if display:
            parts = display.rsplit(" ", 1)
            if len(parts) == 2:
                author_parts.append(f"{parts[1]}, {parts[0]}")
            else:
                author_parts.append(display)
    author_str = bib_escape(" and ".join(author_parts))

    first_author = author_parts[0].split(",")[0] if author_parts else "Unknown"
    key = f"{ascii_key(first_author)}{year}"

    venue = work.get("primary_location") or {}
    source = venue.get("source", {}) or {}
    journal = bib_escape(source.get("display_name", ""))
    entry_type = {"book": "book", "book-chapter": "incollection", "dissertation": "phdthesis",
                  "preprint": "misc", "report": "techreport"}.get(work.get("type", ""), "article")

    lines = [f"@{entry_type}{{{key},"]
    if author_str:
        lines.append(f"  author = {{{author_str}}},")
    lines.append(f"  title = {{{{{title}}}}},")
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
        lines.append(f"  url = {{https://doi.org/{doi}}},")
    lines.append("}")
    return "\n".join(lines)


def minimal_bibtex(pdf_path: str, title: str, author: str, candidates: list[str] | None = None) -> str:
    """Fallback: generate a minimal BibTeX entry from heuristic extraction."""
    stem = Path(pdf_path).stem
    year_match = re.search(r"\b(19|20)\d{2}\b", stem)
    year = year_match.group() if year_match else ""
    key = re.sub(r"[^a-zA-Z0-9]", "", stem)[:20]
    lines = [f"@misc{{{key},"]
    if title:
        lines.append(f"  title = {{{{{bib_escape(title)}}}}},")
    if author:
        lines.append(f"  author = {{{bib_escape(author)}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    lines.append("  note = {[Metadata auto-extracted, verify manually]},")
    if candidates:
        lines.insert(0, "% DOĞRULANMADI: aday künyeler PDF başlığıyla eşleşmedi: " + "; ".join(candidates))
    lines.append("}")
    return "\n".join(lines)


# ── RIS generation ────────────────────────────────────────────────────────────

def bibtex_to_ris_simple(bibtex: str) -> str:
    """Very simple BibTeX → RIS conversion for basic fields."""
    ris_lines = ["TY  - JOUR"]
    for line in bibtex.split("\n"):
        if "author = " in line:
            authors = re.search(r"\{(.+?)\}", line)
            if authors:
                for a in authors.group(1).split(" and "):
                    ris_lines.append(f"AU  - {a.strip()}")
        elif "title = " in line:
            t = re.search(r"\{\{(.+?)\}\}", line)
            if t:
                ris_lines.append(f"TI  - {t.group(1)}")
        elif "year = " in line:
            y = re.search(r"\{(\d{4})\}", line)
            if y:
                ris_lines.append(f"PY  - {y.group(1)}")
        elif "journal = " in line:
            j = re.search(r"\{(.+?)\}", line)
            if j:
                ris_lines.append(f"JO  - {j.group(1)}")
        elif "doi = " in line:
            d = re.search(r"\{(.+?)\}", line)
            if d:
                ris_lines.append(f"DO  - {d.group(1)}")
        elif "volume = " in line:
            v = re.search(r"\{(.+?)\}", line)
            if v:
                ris_lines.append(f"VL  - {v.group(1)}")
        elif "pages = " in line:
            p = re.search(r"\{(.+?)\}", line)
            if p:
                ris_lines.append(f"SP  - {p.group(1)}")
    ris_lines.append("ER  -")
    return "\n".join(ris_lines)


# ── Main processing ───────────────────────────────────────────────────────────

class BibResult:
    def __init__(self, pdf_path: str, bibtex: str, doi: str = "",
                 source: str = "", title: str = "", verified: bool = False):
        self.pdf_path = pdf_path
        self.verified = verified
        self.bibtex = bibtex
        self.doi = doi
        self.source = source  # "crossref" | "openalex" | "heuristic"
        self.title = title


def process_pdf(pdf_path: str, verbose: bool = True) -> BibResult:
    """Extract bibliographic metadata for a single PDF."""
    path = str(pdf_path)
    name = Path(path).name

    if verbose:
        print(f"  Processing: {name}")

    # Step 1: Extract text from first pages
    try:
        text = extract_first_pages(path, max_pages=3)
    except Exception as e:
        if verbose:
            print(f"    ✗ Cannot extract text: {e}")
        return BibResult(path, f"% ERROR: Cannot extract text from {name}\n", source="error")

    # Step 2: Find DOIs
    dois = find_dois(text)
    if verbose and dois:
        print(f"    DOIs found: {dois[:3]}")

    # Step 3: CrossRef lookup for each DOI.
    # İlk sayfalarda başka eserlerin DOI'leri de geçebilir: künye ancak başlığı
    # PDF metninde bulunursa kabul edilir.
    rejected: list[str] = []
    for doi in dois:
        if verbose:
            print(f"    → CrossRef: {doi}")
        try:
            data = fetch_crossref(doi)
        except Exception as e:
            if verbose:
                print(f"      CrossRef error: {e}")
            data = None
        time.sleep(0.2)  # polite rate limiting

        if data:
            title = (data.get("title") or [""])[0]
            if not title_matches_text(title, text):
                rejected.append(f"{doi} ({title[:60]})")
                if verbose:
                    print(f"    ✗ Başlık PDF'te yok, reddedildi: {title[:60]}")
                continue
            bibtex = crossref_to_bibtex(doi, data)
            if verbose:
                print(f"    ✓ CrossRef: {title[:60]}")
            return BibResult(path, bibtex, doi=doi, source="crossref", title=title, verified=True)

    # Step 4: Heuristic title/author extraction + OpenAlex fallback
    if verbose:
        print("    → No DOI found or CrossRef failed. Trying heuristic + OpenAlex...")
    title, author = extract_title_author(text)

    if title:
        for oa_work in search_openalex_many(title):
            oa_title = oa_work.get("title") or ""
            if title_matches_text(oa_title, text):
                bibtex = openalex_to_bibtex(oa_work)
                if verbose:
                    print(f"    ✓ OpenAlex: {oa_title[:60]}")
                return BibResult(path, bibtex, source="openalex", title=oa_title, verified=True)
            rejected.append(f"OpenAlex ({oa_title[:60]})")
        time.sleep(0.1)

    # Step 5: Minimal fallback
    if verbose:
        print("    ⚠ Fallback: minimal entry from filename/heuristics")
    bibtex = minimal_bibtex(path, title, author, candidates=rejected or None)
    return BibResult(path, bibtex, source="heuristic", title=title)


def generate_for_sources(source_dir: str, output_path: str | None = None,
                          fmt: str = "bibtex", verbose: bool = True) -> str:
    """Process all PDFs in a directory, return combined BibTeX/RIS."""
    pdf_files = sorted(Path(source_dir).glob("*.pdf"))
    if not pdf_files:
        pdf_files = sorted(Path(source_dir).glob("*.PDF"))

    if not pdf_files:
        print(f"No PDF files found in {source_dir}")
        return ""

    print(f"\nBibTeX Generator — {len(pdf_files)} PDF(s) in {source_dir}")
    print("=" * 60)

    results = []
    stats = {"crossref": 0, "openalex": 0, "heuristic": 0, "error": 0}

    for pdf in pdf_files:
        result = process_pdf(str(pdf), verbose=verbose)
        results.append(result)
        stats[result.source] = stats.get(result.source, 0) + 1
        print()

    # Combine output
    header_lines = [
        f"% TezAtlas BibTeX — auto-generated from {source_dir}",
        f"% Sources: CrossRef={stats['crossref']}, OpenAlex={stats['openalex']}, "
        f"Heuristic={stats['heuristic']}, Error={stats['error']}",
        "% Review all entries marked [Metadata auto-extracted, verify manually] or DOĞRULANMADI",
        "",
    ]

    if fmt == "ris":
        entries = [bibtex_to_ris_simple(r.bibtex) for r in results]
        combined = "\n\n".join(entries)
    else:
        entries = make_keys_unique([r.bibtex for r in results])
        combined = "\n\n".join(header_lines) + "\n\n".join(entries)

    # Write output
    ext = ".ris" if fmt == "ris" else ".bib"
    if output_path:
        out = Path(output_path)
    else:
        out = Path(source_dir).parent / f"references{ext}"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(combined, encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"Output written to: {out}")
    print(f"  CrossRef:  {stats['crossref']} entries (DOI + başlık PDF'te doğrulandı)")
    print(f"  OpenAlex:  {stats['openalex']} entries (başlık PDF'te doğrulandı)")
    print(f"  Heuristic: {stats['heuristic']} entries (REVIEW REQUIRED)")
    print(f"  Errors:    {stats['error']}")
    return combined


def generate_for_single(pdf_path: str, output_path: str | None = None,
                         fmt: str = "bibtex", verbose: bool = True) -> str:
    """Process a single PDF file."""
    result = process_pdf(pdf_path, verbose=verbose)
    output = result.bibtex
    if fmt == "ris":
        output = bibtex_to_ris_simple(output)

    ext = ".ris" if fmt == "ris" else ".bib"
    if output_path:
        out = Path(output_path)
    else:
        out = Path(pdf_path).with_suffix(ext)

    out.write_text(output, encoding="utf-8")
    print(f"\nOutput: {out}")
    return output


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TezAtlas BibTeX/RIS Generator — extract bibliographic metadata from PDFs"
    )
    parser.add_argument("input", help="PDF file or directory of PDFs")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-named)")
    parser.add_argument("--format", "-f", choices=["bibtex", "ris"], default="bibtex",
                        help="Output format (default: bibtex)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    if not PYMUPDF_AVAILABLE:
        print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
        sys.exit(1)

    p = Path(args.input)
    verbose = not args.quiet

    if p.is_dir():
        generate_for_sources(str(p), args.output, args.format, verbose)
    elif p.is_file() and p.suffix.lower() == ".pdf":
        generate_for_single(str(p), args.output, args.format, verbose)
    else:
        print(f"ERROR: {args.input} is not a PDF file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
