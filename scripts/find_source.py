#!/usr/bin/env python3
"""
find_source.py — TezAtlas Iron Rule 3 Implementation

Multi-provider academic source finder and downloader.
Queries Semantic Scholar, CrossRef, OpenAlex, and arXiv APIs (all free, no key required).
Checks open-access availability via Unpaywall and downloads PDFs to sources/.

Optionally uses any LLM provider configured in agents.yaml (OpenAI, Gemini, DeepSeek,
Groq, Ollama, etc.) for intelligent query expansion via the existing agents system.

Usage:
  # Free-text search (queries all academic APIs)
  python3 scripts/find_source.py "CBDC monetary policy effects"

  # Search in Turkish
  python3 scripts/find_source.py "merkez bankası dijital para politikası"

  # Resolve a specific DOI
  python3 scripts/find_source.py --doi "10.1257/aer.20201073"

  # Download best open-access result to sources/
  python3 scripts/find_source.py "reading saturation" --download

  # Use LLM for query expansion (any provider from agents.yaml)
  python3 scripts/find_source.py "CBDC" --llm-enhance
  python3 scripts/find_source.py "CBDC" --llm-enhance --provider openai

  # Limit results
  python3 scripts/find_source.py "doctoral attrition" --top 5

  # Unpaywall check requires email
  python3 scripts/find_source.py --doi "10.1037/0003-066X.57.3.180" --email you@example.com
"""

from __future__ import annotations

import os
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "sources"

# Polite User-Agent for CrossRef/OpenAlex (they ask for this)
# Crossref/OpenAlex "polite pool" için iletişim adresi (.env: TEZATLAS_MAILTO)
MAILTO = os.environ.get("TEZATLAS_MAILTO", "tezatlas@example.com")
USER_AGENT = f"TezAtlas/1.1 (https://github.com/tialkan/TezAtlas; mailto:{MAILTO})"

# Rate limiting: seconds between requests to each provider
RATE_LIMITS: dict[str, float] = {
    "semantic_scholar": 3.0,   # free tier: 100 req/5min = 1 req/3s
    "crossref": 0.5,
    "openalex": 0.1,
    "arxiv": 1.0,
    "unpaywall": 0.5,
}

_last_request: dict[str, float] = {}


def _throttle(provider: str) -> None:
    """Enforce rate limits per provider."""
    now = time.time()
    wait = RATE_LIMITS.get(provider, 0.5)
    last = _last_request.get(provider, 0.0)
    elapsed = now - last
    if elapsed < wait:
        time.sleep(wait - elapsed)
    _last_request[provider] = time.time()


def _get(url: str, provider: str, timeout: int = 15) -> dict | str | None:
    """HTTP GET with throttling. Returns parsed JSON dict, XML string, or None on error."""
    _throttle(provider)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            content_type = resp.headers.get("Content-Type", "")
            if "xml" in content_type or raw.strip().startswith("<"):
                return raw  # return raw XML string
            return json.loads(raw)
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None


# ── Data Model ────────────────────────────────────────────────────────────────

@dataclass
class SourceResult:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    abstract: str | None = None
    open_access_pdf: str | None = None
    source_api: str = ""
    url: str | None = None

    def short_authors(self) -> str:
        if not self.authors:
            return "?"
        if len(self.authors) == 1:
            return self.authors[0]
        if len(self.authors) == 2:
            return f"{self.authors[0]} & {self.authors[1]}"
        return f"{self.authors[0]} et al."

    def citation_label(self) -> str:
        author = self.authors[0].split()[-1] if self.authors else "?"
        year = self.year or "n.d."
        return f"{author}, {year}"

    def display(self, index: int) -> str:
        lines = [
            f"\n[{index}] {self.title}",
            f"    {self.short_authors()} ({self.year or '?'})  [{self.source_api}]",
        ]
        if self.doi:
            lines.append(f"    DOI: {self.doi}")
        if self.open_access_pdf:
            lines.append(f"    PDF: {self.open_access_pdf}")
        if self.abstract:
            abstract = self.abstract[:200].replace("\n", " ")
            lines.append(f"    {abstract}…")
        return "\n".join(lines)


# ── Semantic Scholar ───────────────────────────────────────────────────────────

def search_semantic_scholar(query: str, limit: int = 5) -> list[SourceResult]:
    fields = "title,authors,year,externalIds,openAccessPdf,abstract"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": fields,
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    data = _get(url, "semantic_scholar")
    if not isinstance(data, dict):
        return []

    results = []
    for item in data.get("data", []):
        doi = (item.get("externalIds") or {}).get("DOI")
        pdf_url = None
        if item.get("openAccessPdf"):
            pdf_url = item["openAccessPdf"].get("url")
        authors = [a.get("name", "") for a in (item.get("authors") or [])]
        results.append(SourceResult(
            title=item.get("title", ""),
            authors=authors,
            year=item.get("year"),
            doi=doi,
            abstract=item.get("abstract"),
            open_access_pdf=pdf_url,
            source_api="SemanticScholar",
        ))
    return results


def get_by_doi_crossref(doi: str) -> SourceResult | None:
    """Direct DOI lookup via CrossRef works/{doi} endpoint."""
    encoded = urllib.parse.quote(doi, safe="")
    url = f"https://api.crossref.org/works/{encoded}"
    data = _get(url, "crossref")
    if not isinstance(data, dict):
        return None
    item = (data.get("message") or {})
    if not item:
        return None
    title_list = item.get("title") or []
    title = title_list[0] if title_list else ""
    if not title:
        return None
    authors = []
    for a in item.get("author") or []:
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            authors.append(name)
    year = None
    pub = item.get("published") or item.get("published-print") or item.get("published-online")
    if pub and pub.get("date-parts"):
        try:
            year = int(pub["date-parts"][0][0])
        except (IndexError, ValueError):
            pass
    abstract_raw = item.get("abstract", "")
    abstract = re.sub(r"<[^>]+>", "", abstract_raw).strip() if abstract_raw else None
    return SourceResult(
        title=title,
        authors=authors,
        year=year,
        doi=item.get("DOI") or doi,
        abstract=abstract,
        source_api="CrossRef",
    )


def get_by_doi_openalex(doi: str) -> SourceResult | None:
    """Direct DOI lookup via OpenAlex."""
    encoded = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
    url = f"https://api.openalex.org/works/{encoded}"
    data = _get(url, "openalex")
    if not isinstance(data, dict) or not data.get("title"):
        return None
    authors = []
    for a in (data.get("authorships") or []):
        name = (a.get("author") or {}).get("display_name", "")
        if name:
            authors.append(name)
    doi_raw = data.get("doi") or ""
    doi_clean = doi_raw.replace("https://doi.org/", "").strip() or doi
    pdf_url = (data.get("open_access") or {}).get("oa_url")
    return SourceResult(
        title=data.get("title", ""),
        authors=authors,
        year=data.get("publication_year"),
        doi=doi_clean,
        open_access_pdf=pdf_url,
        source_api="OpenAlex",
    )


def get_by_doi_semantic_scholar(doi: str) -> SourceResult | None:
    fields = "title,authors,year,externalIds,openAccessPdf,abstract"
    encoded_doi = urllib.parse.quote(doi, safe="")
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{encoded_doi}?fields={fields}"
    data = _get(url, "semantic_scholar")
    if not isinstance(data, dict) or "title" not in data:
        return None
    pdf_url = None
    if data.get("openAccessPdf"):
        pdf_url = data["openAccessPdf"].get("url")
    authors = [a.get("name", "") for a in (data.get("authors") or [])]
    return SourceResult(
        title=data.get("title", ""),
        authors=authors,
        year=data.get("year"),
        doi=doi,
        abstract=data.get("abstract"),
        open_access_pdf=pdf_url,
        source_api="SemanticScholar",
    )


# ── CrossRef ──────────────────────────────────────────────────────────────────

def search_crossref(query: str, limit: int = 5) -> list[SourceResult]:
    params = urllib.parse.urlencode({
        "query": query,
        "rows": limit,
        "select": "DOI,title,author,published,abstract",
        "mailto": MAILTO,
    })
    url = f"https://api.crossref.org/works?{params}"
    data = _get(url, "crossref")
    if not isinstance(data, dict):
        return []

    results = []
    for item in (data.get("message") or {}).get("items", []):
        title_list = item.get("title") or []
        title = title_list[0] if title_list else ""
        authors = []
        for a in item.get("author") or []:
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)
        year = None
        pub = item.get("published") or item.get("published-print")
        if pub and pub.get("date-parts"):
            try:
                year = int(pub["date-parts"][0][0])
            except (IndexError, ValueError):
                pass
        abstract_raw = item.get("abstract", "")
        # CrossRef wraps abstract in JATS XML tags — strip them
        abstract = re.sub(r"<[^>]+>", "", abstract_raw).strip() if abstract_raw else None
        results.append(SourceResult(
            title=title,
            authors=authors,
            year=year,
            doi=item.get("DOI"),
            abstract=abstract,
            source_api="CrossRef",
        ))
    return results


# ── OpenAlex ──────────────────────────────────────────────────────────────────

def search_openalex(query: str, limit: int = 5) -> list[SourceResult]:
    params = urllib.parse.urlencode({
        "search": query,
        "per-page": limit,
        "select": "title,doi,authorships,publication_year,open_access,abstract_inverted_index",
        "mailto": MAILTO,
    })
    url = f"https://api.openalex.org/works?{params}"
    data = _get(url, "openalex")
    if not isinstance(data, dict):
        return []

    results = []
    for item in data.get("results", []):
        authors = []
        for a in (item.get("authorships") or []):
            author_info = a.get("author") or {}
            display_name = author_info.get("display_name", "")
            if display_name:
                authors.append(display_name)
        doi_raw = item.get("doi") or ""
        doi = doi_raw.replace("https://doi.org/", "").strip() or None
        pdf_url = None
        oa = item.get("open_access") or {}
        if oa.get("oa_url"):
            pdf_url = oa["oa_url"]
        # Reconstruct abstract from inverted index
        abstract = _reconstruct_abstract(item.get("abstract_inverted_index"))
        results.append(SourceResult(
            title=item.get("title", ""),
            authors=authors,
            year=item.get("publication_year"),
            doi=doi,
            abstract=abstract,
            open_access_pdf=pdf_url,
            source_api="OpenAlex",
        ))
    return results


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    """OpenAlex stores abstract as {word: [positions]}. Reconstruct to string."""
    if not inverted_index:
        return None
    try:
        word_positions: list[tuple[int, str]] = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(w for _, w in word_positions)
    except Exception:
        return None


# ── arXiv ─────────────────────────────────────────────────────────────────────

def search_arxiv(query: str, limit: int = 5) -> list[SourceResult]:
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "max_results": limit,
        "sortBy": "relevance",
    })
    url = f"https://export.arxiv.org/api/query?{params}"
    raw = _get(url, "arxiv")
    if not isinstance(raw, str):
        return []

    results = []
    try:
        root = ET.fromstring(raw)
        ns = {"atom": "http://www.w3.org/2005/Atom",
              "arxiv": "http://arxiv.org/schemas/atom"}
        for entry in root.findall("atom:entry", ns):
            title = (entry.findtext("atom:title", namespaces=ns) or "").strip().replace("\n", " ")
            abstract = (entry.findtext("atom:summary", namespaces=ns) or "").strip()
            authors = [
                a.findtext("atom:name", namespaces=ns) or ""
                for a in entry.findall("atom:author", ns)
            ]
            # arXiv ID → DOI mapping: try doi element
            doi = entry.findtext("arxiv:doi", namespaces=ns)
            # Year from published date
            published = entry.findtext("atom:published", namespaces=ns) or ""
            year = int(published[:4]) if published else None
            # PDF link
            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href")
                    break
            results.append(SourceResult(
                title=title,
                authors=authors,
                year=year,
                doi=doi,
                abstract=abstract[:400] if abstract else None,
                open_access_pdf=pdf_url,
                source_api="arXiv",
            ))
    except ET.ParseError:
        pass
    return results


# ── Unpaywall ─────────────────────────────────────────────────────────────────

def get_oa_url_unpaywall(doi: str, email: str) -> str | None:
    """Check Unpaywall for an open-access PDF URL for a given DOI."""
    encoded = urllib.parse.quote(doi, safe="")
    url = f"https://api.unpaywall.org/v2/{encoded}?email={urllib.parse.quote(email)}"
    data = _get(url, "unpaywall")
    if not isinstance(data, dict):
        return None
    best_oa = data.get("best_oa_location") or {}
    return best_oa.get("url_for_pdf") or best_oa.get("url")


# ── PDF Downloader ─────────────────────────────────────────────────────────────

def sanitize_filename(s: str) -> str:
    """Convert title to safe filename."""
    s = re.sub(r"[^\w\s-]", "", s.lower())
    s = re.sub(r"[\s_-]+", "_", s.strip())
    return s[:80]


def download_pdf(url: str, output_path: Path, timeout: int = 30) -> bool:
    """Download a PDF from url to output_path. Returns True on success."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower() and not url.endswith(".pdf"):
                # Try anyway — some servers don't set content-type correctly
                pass
            data = resp.read()
            if len(data) < 1024:
                return False  # Too small, probably an error page
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(data)
            return True
    except (urllib.error.URLError, OSError):
        return False


# ── LLM Query Expansion ───────────────────────────────────────────────────────

def llm_expand_query(query: str, provider: str | None, field: str) -> list[str]:
    """
    Use the configured LLM (any provider in agents.yaml) to expand the search query
    into better academic search terms. Works with OpenAI, Gemini, DeepSeek, Ollama, etc.

    Calls the existing source_hunter agent via agents/run.py.
    Returns a list of expanded queries; falls back to [query] on failure.
    """
    cmd = [
        sys.executable,
        str(REPO_ROOT / "agents" / "run.py"),
        "source_hunter",
        "--research-question", query,
        "--field", field,
        "--top", "3",
    ]
    if provider:
        cmd += ["--provider", provider]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            return [query]
        # Parse JSON output from source_hunter
        output = result.stdout.strip()
        # Find JSON block
        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            keywords = data.get("search_keywords") or []
            if keywords:
                return keywords[:5]
        return [query]
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return [query]


# ── Main Search Orchestration ─────────────────────────────────────────────────

def search_all(query: str, limit_per_provider: int = 5) -> list[SourceResult]:
    """Search all academic API providers and return merged, deduplicated results."""
    all_results: list[SourceResult] = []
    providers = [
        ("Semantic Scholar", search_semantic_scholar),
        ("CrossRef", search_crossref),
        ("OpenAlex", search_openalex),
        ("arXiv", search_arxiv),
    ]
    for name, fn in providers:
        print(f"  Searching {name}…", end=" ", flush=True)
        try:
            results = fn(query, limit_per_provider)
            print(f"{len(results)} results")
            all_results.extend(results)
        except Exception as e:
            print(f"error ({e})")

    # Deduplicate by DOI (prefer results with open-access PDF)
    seen_dois: dict[str, SourceResult] = {}
    no_doi: list[SourceResult] = []
    for r in all_results:
        if r.doi:
            key = r.doi.lower().strip()
            existing = seen_dois.get(key)
            if existing is None or (r.open_access_pdf and not existing.open_access_pdf):
                seen_dois[key] = r
        else:
            no_doi.append(r)

    return list(seen_dois.values()) + no_doi


def find_best_pdf(result: SourceResult, email: str | None) -> str | None:
    """Find the best PDF URL for a result, trying all available sources."""
    # 1. Already have a direct PDF URL
    if result.open_access_pdf:
        return result.open_access_pdf
    # 2. Try Unpaywall if we have a DOI and email
    if result.doi and email:
        print(f"  Checking Unpaywall for DOI {result.doi}…", end=" ", flush=True)
        url = get_oa_url_unpaywall(result.doi, email)
        if url:
            print("found")
            return url
        print("not found")
    return None


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas Iron Rule 3 — Academic Source Finder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("query", nargs="?", help="Free-text search query")
    parser.add_argument("--doi", help="Resolve a specific DOI directly")
    parser.add_argument("--download", action="store_true",
                        help="Download best open-access PDF to sources/")
    parser.add_argument("--output", type=Path, default=SOURCES_DIR,
                        help="Directory to save downloaded PDFs (default: sources/)")
    parser.add_argument("--top", type=int, default=10,
                        help="Maximum results to show (default: 10)")
    parser.add_argument("--llm-enhance", action="store_true",
                        help="Use LLM agent to expand query (uses agents.yaml provider)")
    parser.add_argument("--provider", help="LLM provider for --llm-enhance (e.g. openai, gemini)")
    parser.add_argument("--field", default="general",
                        help="Research field for LLM enhancement (default: general)")
    parser.add_argument("--email", help="Email for Unpaywall API (optional)")

    args = parser.parse_args()

    if not args.query and not args.doi:
        parser.print_help()
        sys.exit(1)

    print("\nTezAtlas — Iron Rule 3: Source Finder")
    print("══════════════════════════════════════")

    # ── DOI mode ──────────────────────────────────────────────────────────────
    if args.doi:
        print(f"\nLooking up DOI: {args.doi}")
        result = None
        for label, fn in [
            ("Semantic Scholar", get_by_doi_semantic_scholar),
            ("CrossRef",         get_by_doi_crossref),
            ("OpenAlex",         get_by_doi_openalex),
        ]:
            print(f"  Trying {label}…", end=" ", flush=True)
            result = fn(args.doi)
            if result:
                print("found")
                break
            print("not found")
        if result is None:
            print("✗ DOI not found in any provider.")
            sys.exit(1)
        print(result.display(1))
        if args.download:
            _download_result(result, args.output, args.email)
        return

    # ── Text search mode ───────────────────────────────────────────────────────
    queries = [args.query]

    if args.llm_enhance:
        print(f"\nExpanding query with LLM (provider: {args.provider or 'from agents.yaml'})…")
        expanded = llm_expand_query(args.query, args.provider, args.field)
        if expanded != [args.query]:
            print(f"  Expanded queries: {expanded}")
            queries = expanded
        else:
            print("  (LLM expansion unavailable, using original query)")

    all_results: list[SourceResult] = []
    for q in queries:
        print(f'\nSearching: "{q}"')
        results = search_all(q, limit_per_provider=max(3, args.top // len(queries)))
        all_results.extend(results)

    # Deduplicate across expanded queries
    seen: dict[str, SourceResult] = {}
    final: list[SourceResult] = []
    for r in all_results:
        key = (r.doi or r.title).lower().strip()
        if key not in seen:
            seen[key] = r
            final.append(r)

    final = final[:args.top]

    if not final:
        print("\n✗ No results found. Try a different query or --llm-enhance.")
        sys.exit(1)

    print(f"\n{'─'*50}")
    print(f"  {len(final)} results found")
    print(f"{'─'*50}")

    for i, result in enumerate(final, 1):
        print(result.display(i))

    oa_count = sum(1 for r in final if r.open_access_pdf)
    print(f"\n  {oa_count}/{len(final)} results have open-access PDFs")

    if args.download:
        print("\nDownloading open-access PDFs…")
        downloaded = 0
        paywalled = []
        for result in final:
            if _download_result(result, args.output, args.email):
                downloaded += 1
            elif result.doi:
                paywalled.append(result)
        print(f"\n✅ Downloaded {downloaded}/{len(final)} PDFs to {args.output}")
        if paywalled:
            print(f"\n⚠️  {len(paywalled)} kaynak açık erişimde bulunamadı — kütüphane erişimi gerekiyor:")
            for r in paywalled:
                doi_link = f"https://doi.org/{r.doi}" if r.doi else ""
                print(f"   • {r.title[:70]}")
                print(f"     {r.short_authors()} ({r.year or '?'})")
                if doi_link:
                    print(f"     DOI: {doi_link}")
            print("\n   Bu kaynaklara erişim için:")
            print("   1. Üniversite kütüphane proxy'si üzerinden doi.org/10.xxxx linkini aç")
            print("   2. Google Scholar → 'Tüm N sürüm' → ücretsiz PDF ara")
            print("   3. Unpaywall tarayıcı eklentisi (unpaywall.org) — otomatik bulur")
            print("   4. Yazara e-posta: ResearchGate profilinde 'Request full-text' butonu")
            print("   5. Kütüphaneler arası ödünç ya da yazardan isteme")
    else:
        if oa_count > 0:
            print("\nTip: Add --download to save open-access PDFs to sources/")
        non_oa = [r for r in final if not r.open_access_pdf]
        if non_oa:
            print(f"\n⚠️  {len(non_oa)} kaynak açık erişimde değil. Kütüphane erişimi için:")
            print("   • Üniversite VPN + kütüphane proxy")
            print("   • scholar.google.com → PDF linkini ara")
            print("   • Kurum kütüphanesi / kütüphaneler arası ödünç")
            print("   • unpaywall.org tarayıcı eklentisi")
        print("\n   Bulduğun PDF'leri sources/ klasörüne ekle, sonra gate'i yeniden kontrol et.")


def _download_result(result: SourceResult, output_dir: Path, email: str | None) -> bool:
    """Download PDF for a single result. Returns True on success."""
    pdf_url = find_best_pdf(result, email)
    if not pdf_url:
        print(f"  ✗ No open-access PDF: {result.title[:60]}")
        return False
    fname = sanitize_filename(result.title)
    if result.year:
        fname = f"{fname}_{result.year}"
    output_path = output_dir / f"{fname}.pdf"
    if output_path.exists():
        print(f"  ↩ Already exists: {output_path.name}")
        return True
    print(f"  ↓ Downloading: {result.title[:60]}…", end=" ", flush=True)
    if download_pdf(pdf_url, output_path):
        size_kb = output_path.stat().st_size // 1024
        print(f"✓ ({size_kb} KB) → {output_path.name}")
        return True
    else:
        print("✗ download failed")
        return False


if __name__ == "__main__":
    main()
