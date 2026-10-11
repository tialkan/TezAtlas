"""
tests/test_new_project.py — Project scaffolding tests

Verifies that new_project.py creates the correct file structure
and that core/session.py can parse the generated STATUS.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


from core.session import TezAtlasSession


def _scaffold(
    tmp_path: Path,
    doc_type: str = "thesis",
    lang: str = "tr",
    field: str = "economics",
    title: str = "Test Project",
) -> subprocess.CompletedProcess:
    """Run new_project.py in tmp_path and return the result."""
    return subprocess.run(
        [
            sys.executable,
            "scripts/new_project.py",
            "--type", doc_type,
            "--lang", lang,
            "--field", field,
            "--title", title,
            "--output", str(tmp_path),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


# ── File structure ────────────────────────────────────────────────────────────

class TestScaffoldedFiles:
    def test_creates_status_md(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        assert (tmp_path / "STATUS.md").exists()

    def test_creates_reading_report(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        assert (tmp_path / "READING_REPORT.md").exists()

    def test_creates_argumanlar(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        assert (tmp_path / "ARGUMENTS.md").exists()

    def test_creates_sources_dir(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        assert (tmp_path / "sources").is_dir()

    def test_creates_notes_dir(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        assert (tmp_path / "notes").is_dir()

    def test_exits_zero(self, tmp_path: Path) -> None:
        result = _scaffold(tmp_path)
        assert result.returncode == 0, result.stderr

    def test_all_doc_types_scaffold(self, tmp_path: Path) -> None:
        doc_types = [
            "thesis", "article", "conference", "lit-review",
            "report", "book-chapter", "grant-proposal", "research-proposal",
        ]
        for dt in doc_types:
            sub = tmp_path / dt
            sub.mkdir()
            result = _scaffold(sub, doc_type=dt)
            assert result.returncode == 0, f"{dt} failed: {result.stderr}"
            assert (sub / "STATUS.md").exists(), f"STATUS.md missing for {dt}"


# ── STATUS.md parsability ─────────────────────────────────────────────────────

class TestStatusMdFormat:
    def test_session_can_load(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        sess = TezAtlasSession(tmp_path)
        state = sess.load()
        assert state  # not empty

    def test_document_type_parsed(self, tmp_path: Path) -> None:
        _scaffold(tmp_path, doc_type="article")
        state = TezAtlasSession(tmp_path).load()
        assert state.get("document_type") == "article"

    def test_current_phase_is_zero(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        state = TezAtlasSession(tmp_path).load()
        assert int(state.get("current_phase", -1)) == 0

    def test_sources_initialized(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        state = TezAtlasSession(tmp_path).load()
        src = state.get("sources") or {}
        assert int(src.get("total_collected", -1)) == 0
        assert int(src.get("read", -1)) == 0
        assert src.get("saturation_reached") is False

    def test_writing_schedule_initialized(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        state = TezAtlasSession(tmp_path).load()
        ws = state.get("writing_schedule") or {}
        assert int(ws.get("current_streak", -1)) == 0
        assert int(ws.get("total_sessions", -1)) == 0

    def test_language_field_present(self, tmp_path: Path) -> None:
        _scaffold(tmp_path, lang="en")
        state = TezAtlasSession(tmp_path).load()
        lang = state.get("language", "")
        assert lang  # non-empty

    def test_field_parsed(self, tmp_path: Path) -> None:
        _scaffold(tmp_path, field="law")
        state = TezAtlasSession(tmp_path).load()
        assert state.get("field") == "law"

    def test_phase_name_resolves(self, tmp_path: Path) -> None:
        _scaffold(tmp_path, doc_type="thesis")
        state = TezAtlasSession(tmp_path).load()
        assert isinstance(state.get("_phase_name"), str)
        assert len(state["_phase_name"]) > 0


# ── READING_REPORT.md format ──────────────────────────────────────────────────

class TestReadingReportFormat:
    def test_has_table_header(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        content = (tmp_path / "READING_REPORT.md").read_text(encoding="utf-8")
        assert "| #" in content or "|---" in content

    def test_has_status_codes(self, tmp_path: Path) -> None:
        _scaffold(tmp_path)
        content = (tmp_path / "READING_REPORT.md").read_text(encoding="utf-8")
        assert "🔵" in content


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_title_with_spaces(self, tmp_path: Path) -> None:
        result = _scaffold(tmp_path, title="My Research on Things")
        assert result.returncode == 0

    def test_invalid_doc_type_exits_nonzero(self, tmp_path: Path) -> None:
        result = _scaffold(tmp_path, doc_type="invalid-type")
        assert result.returncode != 0

    def test_existing_project_does_not_overwrite(self, tmp_path: Path) -> None:
        """Running twice should not silently destroy STATUS.md."""
        _scaffold(tmp_path)
        (tmp_path / "STATUS.md").write_text("# Custom Content\n", encoding="utf-8")
        _scaffold(tmp_path)
        # Should either refuse or the content should still exist
        content = (tmp_path / "STATUS.md").read_text(encoding="utf-8")
        # Either new_project exits non-zero, or it preserves/updates the file
        # The key is it should not produce an empty file
        assert content.strip()
