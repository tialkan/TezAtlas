"""
TezAtlas Academic API Clients
------------------------------
Thin, dependency-free wrappers for:
  - Semantic Scholar  (paper search, citation graph, author lookup)
  - OpenAlex          (open access metadata, institution data)
  - CrossRef          (DOI resolution, BibTeX generation)

All clients use urllib only — no external HTTP dependencies.
"""

import os
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

# Polite pool identifier for rate-limited APIs
# Crossref/OpenAlex "polite pool" için iletişim adresi (.env: TEZATLAS_MAILTO)
MAILTO = os.environ.get("TEZATLAS_MAILTO", "tezatlas@example.com")
USER_AGENT = f"TezAtlas/1.1 (https://github.com/tialkan/TezAtlas; mailto:{MAILTO})"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get(url: str, params: dict | None = None, headers: dict | None = None,
         timeout: int = 15) -> dict | list | None:
    """Make a GET request, return parsed JSON or None on error."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    for deneme in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            # Hız sınırı ya da geçici sunucu hatası: Retry-After'a uyarak en fazla iki kez daha dene
            if e.code in (429, 500, 502, 503, 504) and deneme < 2:
                bekle = e.headers.get("Retry-After") if e.headers else None
                time.sleep(min(float(bekle), 30.0) if bekle and bekle.isdigit() else 2 ** (deneme + 1))
                continue
            raise
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            return None
    return None


def _format_authors(author_list: list[dict], key_family: str = "family",
                    key_given: str = "given") -> str:
    """Format list of author dicts to 'Family, Given and ...' string."""
    parts = []
    for a in author_list[:8]:  # cap at 8 for display
        family = a.get(key_family, "")
        given = a.get(key_given, "")
        parts.append(f"{family}, {given}".strip(", ") if family else given)
    result = " and ".join(parts)
    if len(author_list) > 8:
        result += " et al."
    return result


# ── CrossRef ──────────────────────────────────────────────────────────────────

class CrossRefClient:
    """
    CrossRef REST API client.
    Docs: https://api.crossref.org/swagger-ui/index.html
    """
    BASE = "https://api.crossref.org"

    def works_by_doi(self, doi: str) -> dict | None:
        """Fetch full metadata for a DOI. Returns CrossRef 'message' dict."""
        data = _get(f"{self.BASE}/works/{urllib.parse.quote(doi, safe='')}")
        if data and "message" in data:
            return data["message"]
        return None

    def works_query(self, query: str, rows: int = 10,
                    filter_type: str | None = None) -> list[dict]:
        """Full-text query across CrossRef. Returns list of works."""
        params: dict[str, Any] = {"query": query, "rows": rows,
                                   "mailto": MAILTO}
        if filter_type:
            params["filter"] = f"type:{filter_type}"
        data = _get(f"{self.BASE}/works", params=params)
        if data and "message" in data:
            return data["message"].get("items", [])
        return []

    def to_bibtex(self, doi: str) -> str | None:
        """Get BibTeX for a DOI via CrossRef content negotiation."""
        url = f"https://doi.org/{urllib.parse.quote(doi, safe='')}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/x-bibtex")
        req.add_header("User-Agent", USER_AGENT)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8")
        except Exception:
            return None

    def format_work(self, work: dict) -> dict:
        """Normalize a CrossRef work dict to TezAtlas standard format."""
        authors_raw = work.get("author", [])
        year_info = work.get("published", work.get("published-print", {}))
        year = str(year_info.get("date-parts", [[""]])[0][0]) if year_info else ""
        container = work.get("container-title", [""])
        return {
            "title": work.get("title", [""])[0] if work.get("title") else "",
            "authors": _format_authors(authors_raw),
            "year": year,
            "doi": work.get("DOI", ""),
            "url": f"https://doi.org/{work.get('DOI', '')}",
            "journal": container[0] if container else "",
            "volume": work.get("volume", ""),
            "issue": work.get("issue", ""),
            "pages": work.get("page", ""),
            "publisher": work.get("publisher", ""),
            "type": work.get("type", ""),
            "abstract": work.get("abstract", ""),
            "source": "crossref",
        }


# ── Semantic Scholar ──────────────────────────────────────────────────────────

class SemanticScholarClient:
    """
    Semantic Scholar API client.
    Docs: https://api.semanticscholar.org/graph/v1
    Rate limit: 100 req/5min unauthenticated; add S2_API_KEY for 1 req/sec.
    """
    BASE = "https://api.semanticscholar.org/graph/v1"
    PAPER_FIELDS = (
        "paperId,title,authors,year,abstract,externalIds,"
        "publicationVenue,openAccessPdf,citationCount,"
        "influentialCitationCount,fieldsOfStudy"
    )
    CITATION_FIELDS = "paperId,title,authors,year,externalIds,citationCount"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def _headers(self) -> dict:
        h = {}
        if self.api_key:
            h["x-api-key"] = self.api_key
        return h

    def search_papers(self, query: str, limit: int = 10,
                      fields_of_study: list[str] | None = None) -> list[dict]:
        """Search papers by keyword. Returns list of normalized paper dicts."""
        params: dict[str, Any] = {
            "query": query,
            "limit": min(limit, 100),
            "fields": self.PAPER_FIELDS,
        }
        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)
        data = _get(f"{self.BASE}/paper/search", params=params,
                    headers=self._headers())
        if not data:
            return []
        return [self._format_paper(p) for p in data.get("data", [])]

    def get_paper(self, paper_id: str) -> dict | None:
        """Get paper details by Semantic Scholar paperId or DOI:xxx or arXiv:xxx."""
        data = _get(f"{self.BASE}/paper/{urllib.parse.quote(paper_id, safe=':')}",
                    params={"fields": self.PAPER_FIELDS}, headers=self._headers())
        return self._format_paper(data) if data else None

    def get_citations(self, paper_id: str, limit: int = 20) -> list[dict]:
        """Papers that cite this paper (incoming citations)."""
        data = _get(
            f"{self.BASE}/paper/{urllib.parse.quote(paper_id, safe=':')}/citations",
            params={"limit": limit, "fields": self.CITATION_FIELDS},
            headers=self._headers(),
        )
        if not data:
            return []
        return [self._format_paper(c.get("citingPaper", {}))
                for c in data.get("data", [])]

    def get_references(self, paper_id: str, limit: int = 50) -> list[dict]:
        """Papers that this paper cites (outgoing references)."""
        data = _get(
            f"{self.BASE}/paper/{urllib.parse.quote(paper_id, safe=':')}/references",
            params={"limit": limit, "fields": self.CITATION_FIELDS},
            headers=self._headers(),
        )
        if not data:
            return []
        return [self._format_paper(r.get("citedPaper", {}))
                for r in data.get("data", [])]

    def search_author(self, name: str, limit: int = 5) -> list[dict]:
        """Search for an author by name."""
        data = _get(
            f"{self.BASE}/author/search",
            params={"query": name, "limit": limit,
                    "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex"},
            headers=self._headers(),
        )
        if not data:
            return []
        return data.get("data", [])

    def _format_paper(self, p: dict) -> dict:
        """Normalize a S2 paper dict to TezAtlas standard format."""
        if not p:
            return {}
        ext_ids = p.get("externalIds", {}) or {}
        doi = ext_ids.get("DOI", "")
        venue = p.get("publicationVenue") or {}
        pdf_info = p.get("openAccessPdf") or {}
        authors = p.get("authors", []) or []
        author_str = " and ".join(
            a.get("name", "") for a in authors[:8]
        )
        if len(authors) > 8:
            author_str += " et al."
        return {
            "title": p.get("title", ""),
            "authors": author_str,
            "year": str(p.get("year", "")),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}",
            "journal": venue.get("name", ""),
            "citation_count": p.get("citationCount", 0),
            "influential_citations": p.get("influentialCitationCount", 0),
            "fields": p.get("fieldsOfStudy") or [],
            "abstract": (p.get("abstract") or "")[:500],
            "open_access_pdf": pdf_info.get("url", ""),
            "paper_id": p.get("paperId", ""),
            "source": "semantic_scholar",
        }


# ── OpenAlex ──────────────────────────────────────────────────────────────────

class OpenAlexClient:
    """
    OpenAlex API client.
    Docs: https://docs.openalex.org
    Free, no API key needed. Rate limit: 10 req/sec with mailto header.
    """
    BASE = "https://api.openalex.org"

    def search_works(self, query: str, limit: int = 10,
                     open_access: bool = False,
                     publication_year: int | None = None) -> list[dict]:
        """Search OpenAlex works."""
        params: dict[str, Any] = {
            "search": query,
            "per-page": min(limit, 50),
            "mailto": MAILTO,
        }
        filters = []
        if open_access:
            filters.append("is_oa:true")
        if publication_year:
            filters.append(f"publication_year:{publication_year}")
        if filters:
            params["filter"] = ",".join(filters)

        data = _get(f"{self.BASE}/works", params=params)
        if not data:
            return []
        return [self._format_work(w) for w in data.get("results", [])]

    def get_work_by_doi(self, doi: str) -> dict | None:
        """Fetch OpenAlex work by DOI."""
        clean = doi.replace("https://doi.org/", "").strip()
        data = _get(f"{self.BASE}/works/https://doi.org/{urllib.parse.quote(clean, safe='')}")
        return self._format_work(data) if data and data.get("id") else None

    def get_author(self, author_id: str) -> dict | None:
        """Fetch author profile by OpenAlex author ID or ORCID."""
        data = _get(f"{self.BASE}/authors/{urllib.parse.quote(author_id, safe=':/')}")
        return data

    def search_authors(self, name: str, limit: int = 5) -> list[dict]:
        """Search authors by name."""
        params = {"search": name, "per-page": limit,
                  "mailto": MAILTO}
        data = _get(f"{self.BASE}/authors", params=params)
        if not data:
            return []
        return data.get("results", [])

    def get_institution(self, institution_id: str) -> dict | None:
        """Fetch institution metadata by OpenAlex ID or ROR."""
        data = _get(f"{self.BASE}/institutions/{institution_id}")
        return data

    def _format_work(self, w: dict) -> dict:
        """Normalize OpenAlex work to TezAtlas standard format."""
        if not w:
            return {}
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        authorships = w.get("authorships", []) or []
        authors = " and ".join(
            a.get("author", {}).get("display_name", "")
            for a in authorships[:8]
        )
        if len(authorships) > 8:
            authors += " et al."
        location = (w.get("primary_location") or {})
        source = (location.get("source") or {})
        oa_url = (location.get("pdf_url") or "")
        concepts = [c.get("display_name", "") for c in (w.get("concepts") or [])[:5]]
        return {
            "title": w.get("title", ""),
            "authors": authors,
            "year": str(w.get("publication_year", "")),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else w.get("id", ""),
            "journal": source.get("display_name", ""),
            "open_access": w.get("open_access", {}).get("is_oa", False),
            "open_access_pdf": oa_url,
            "citation_count": w.get("cited_by_count", 0),
            "concepts": concepts,
            "abstract": "",  # OpenAlex doesn't return abstract in search
            "source": "openalex",
        }


# ── Aggregated search ─────────────────────────────────────────────────────────

class AcademicSearch:
    """
    Unified search across multiple academic APIs.
    Returns merged, deduplicated results ranked by citation count.
    """

    def __init__(self, s2_api_key: str | None = None):
        self.crossref = CrossRefClient()
        self.s2 = SemanticScholarClient(api_key=s2_api_key)
        self.openalex = OpenAlexClient()

    def search(self, query: str, limit_per_source: int = 5,
               sources: list[str] | None = None) -> list[dict]:
        """
        Search across all sources and merge results.
        sources: subset of ["s2", "openalex", "crossref"] or None for all.
        """
        if sources is None:
            sources = ["s2", "openalex", "crossref"]

        all_results: list[dict] = []
        # Bir kaynak hata verirse sessizce "sonuç yok" denmez; hata kullanıcıya bildirilir.
        self.son_hatalar: list[str] = []

        if "s2" in sources:
            try:
                all_results.extend(self.s2.search_papers(query, limit=limit_per_source))
                time.sleep(0.2)
            except Exception as hata:
                self.son_hatalar.append(f"{type(hata).__name__}: {hata}"[:200])

        if "openalex" in sources:
            try:
                all_results.extend(self.openalex.search_works(query, limit=limit_per_source))
                time.sleep(0.1)
            except Exception as hata:
                self.son_hatalar.append(f"{type(hata).__name__}: {hata}"[:200])

        if "crossref" in sources:
            try:
                works = self.crossref.works_query(query, rows=limit_per_source)
                all_results.extend([self.crossref.format_work(w) for w in works])
                time.sleep(0.2)
            except Exception as hata:
                self.son_hatalar.append(f"{type(hata).__name__}: {hata}"[:200])

        # Deduplicate by DOI
        seen_dois: set[str] = set()
        deduped: list[dict] = []
        for r in all_results:
            doi = r.get("doi", "").lower()
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            deduped.append(r)

        # Sort by citation count (descending)
        deduped.sort(key=lambda x: x.get("citation_count", 0), reverse=True)
        return deduped

    def doi_to_bibtex(self, doi: str) -> str | None:
        """Get BibTeX for a DOI — tries CrossRef content negotiation first."""
        bibtex = self.crossref.to_bibtex(doi)
        if bibtex:
            return bibtex
        # Fallback: fetch metadata and format manually
        work = self.crossref.works_by_doi(doi)
        if work:
            from tools.bibtex_generator import crossref_to_bibtex
            return crossref_to_bibtex(doi, work)
        return None
