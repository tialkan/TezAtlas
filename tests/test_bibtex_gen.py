"""
tests/test_bibtex_gen.py — BibTeX generator tests (tools/bibtex_generator.py)

Tests DOI extraction, BibTeX formatting, OpenAlex conversion, RIS export,
and heuristic fallback. No network calls are made (offline tests only).
"""

from __future__ import annotations



from tools.bibtex_generator import (
    find_dois,
    crossref_to_bibtex,
    openalex_to_bibtex,
    minimal_bibtex,
    extract_title_author,
    bibtex_to_ris_simple,
)


# ── find_dois ─────────────────────────────────────────────────────────────────

class TestFindDois:
    def test_simple_doi(self) -> None:
        text = "This paper has DOI: 10.1234/example.2023"
        assert "10.1234/example.2023" in find_dois(text)

    def test_doi_with_trailing_punctuation(self) -> None:
        text = "See doi: 10.1038/nature12345."
        dois = find_dois(text)
        assert dois
        assert not dois[0].endswith(".")

    def test_doi_in_url(self) -> None:
        text = "https://doi.org/10.1016/j.socscimed.2021.113 was the source"
        dois = find_dois(text)
        assert dois
        assert dois[0].startswith("10.")

    def test_no_doi(self) -> None:
        assert find_dois("This paper has no DOI.") == []

    def test_multiple_dois_deduplicated(self) -> None:
        text = "10.1234/first and 10.1234/first again and 10.5678/second"
        dois = find_dois(text)
        assert len(dois) == 2
        assert dois[0] == "10.1234/first"

    def test_doi_with_hyphens(self) -> None:
        text = "DOI 10.1111/j.1365-2656.2009.01622.x was cited"
        dois = find_dois(text)
        assert dois
        assert "10.1111" in dois[0]

    def test_returns_list(self) -> None:
        assert isinstance(find_dois(""), list)


# ── crossref_to_bibtex ────────────────────────────────────────────────────────

class TestCrossrefToBibtex:
    def _article_data(self) -> dict:
        return {
            "type": "journal-article",
            "title": ["Causal Inference in Economics"],
            "author": [
                {"family": "Angrist", "given": "Joshua"},
                {"family": "Pischke", "given": "Jörn-Steffen"},
            ],
            "published": {"date-parts": [[2010, 1]]},
            "container-title": ["Journal of Economic Perspectives"],
            "volume": "24",
            "issue": "2",
            "page": "3-30",
            "publisher": "American Economic Association",
        }

    def test_generates_article_type(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "@article{" in bib

    def test_contains_doi_url(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "10.1257/jep.24.2.3" in bib
        assert "doi.org" in bib

    def test_contains_both_authors(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "Angrist" in bib
        assert "Pischke" in bib

    def test_contains_title(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "Causal Inference" in bib

    def test_contains_year(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "2010" in bib

    def test_citekey_format(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "Angrist2010" in bib

    def test_journal_present(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert "Journal of Economic Perspectives" in bib

    def test_book_chapter_type(self) -> None:
        data = dict(self._article_data())
        data["type"] = "book-chapter"
        bib = crossref_to_bibtex("10.1234/test", data)
        assert "@incollection{" in bib

    def test_unknown_type_falls_back_to_misc(self) -> None:
        data = dict(self._article_data())
        data["type"] = "unknown-type"
        bib = crossref_to_bibtex("10.1234/test", data)
        assert "@misc{" in bib

    def test_balanced_braces(self) -> None:
        bib = crossref_to_bibtex("10.1257/jep.24.2.3", self._article_data())
        assert bib.count("{") == bib.count("}")


# ── openalex_to_bibtex ────────────────────────────────────────────────────────

class TestOpenalexToBibtex:
    def _work(self) -> dict:
        return {
            "title": "The Productivity Paradox",
            "publication_year": 2019,
            "doi": "https://doi.org/10.1000/xyz123",
            "authorships": [
                {"author": {"display_name": "Robert Solow"}},
                {"author": {"display_name": "Paul Romer"}},
            ],
            "primary_location": {
                "source": {"display_name": "American Economic Review"}
            },
        }

    def test_generates_article_type(self) -> None:
        bib = openalex_to_bibtex(self._work())
        assert "@article{" in bib

    def test_contains_title(self) -> None:
        bib = openalex_to_bibtex(self._work())
        assert "Productivity Paradox" in bib

    def test_contains_year(self) -> None:
        bib = openalex_to_bibtex(self._work())
        assert "2019" in bib

    def test_doi_stripped_prefix(self) -> None:
        bib = openalex_to_bibtex(self._work())
        assert "10.1000/xyz123" in bib

    def test_empty_work_no_crash(self) -> None:
        bib = openalex_to_bibtex({})
        assert "@article{" in bib


# ── minimal_bibtex ────────────────────────────────────────────────────────────

class TestMinimalBibtex:
    def test_generates_misc_type(self) -> None:
        bib = minimal_bibtex("sources/unknown_paper.pdf", "Some Title", "John Smith")
        assert "@misc{" in bib

    def test_includes_manual_review_note(self) -> None:
        bib = minimal_bibtex("sources/paper.pdf", "", "")
        assert "verify manually" in bib.lower() or "Metadata" in bib

    def test_extracts_year_from_filename(self) -> None:
        bib = minimal_bibtex("sources/smith_2022_paper.pdf", "Title", "Smith")
        assert "2022" in bib

    def test_no_crash_on_empty(self) -> None:
        bib = minimal_bibtex("unknown.pdf", "", "")
        assert bib


# ── extract_title_author ──────────────────────────────────────────────────────

class TestExtractTitleAuthor:
    def test_extracts_long_title(self) -> None:
        text = "\n\nThe Effects of Monetary Policy on Economic Growth\n\nJohn Smith\n\nAbstract..."
        title, _ = extract_title_author(text)
        assert "Monetary Policy" in title

    def test_empty_text(self) -> None:
        title, author = extract_title_author("")
        assert title == ""
        assert author == ""

    def test_returns_tuple(self) -> None:
        result = extract_title_author("some text")
        assert isinstance(result, tuple)
        assert len(result) == 2


# ── bibtex_to_ris_simple ─────────────────────────────────────────────────────

class TestBibtexToRis:
    def _sample_bibtex(self) -> str:
        return (
            "@article{Smith2020,\n"
            "  author = {Smith, John and Doe, Jane},\n"
            "  title = {{The Study of Things}},\n"
            "  journal = {Nature},\n"
            "  year = {2020},\n"
            "  volume = {10},\n"
            "  pages = {1-20},\n"
            "  doi = {10.1234/test},\n"
            "}"
        )

    def test_starts_with_ty(self) -> None:
        ris = bibtex_to_ris_simple(self._sample_bibtex())
        assert ris.startswith("TY  -")

    def test_ends_with_er(self) -> None:
        ris = bibtex_to_ris_simple(self._sample_bibtex())
        assert ris.strip().endswith("ER  -")

    def test_contains_author(self) -> None:
        ris = bibtex_to_ris_simple(self._sample_bibtex())
        assert "AU  -" in ris

    def test_contains_year(self) -> None:
        ris = bibtex_to_ris_simple(self._sample_bibtex())
        assert "2020" in ris

    def test_contains_doi(self) -> None:
        ris = bibtex_to_ris_simple(self._sample_bibtex())
        assert "10.1234/test" in ris
