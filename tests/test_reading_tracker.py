"""
tests/test_reading_tracker.py — Reading Tracker tests

Tests READING_REPORT.md parsing, sync, and mark commands.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scripts.reading_tracker import (
    _parse_table,
    _write_report,
    STATUS_POOL,
    STATUS_DONE,
    STATUS_DEFERRED,
    cmd_sync,
    cmd_mark,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

MINIMAL_REPORT = textwrap.dedent("""\
    # READING_REPORT.md — Okuma Raporu

    **Proje:** Test

    ## Kaynak Envanteri

    | # | Yazar(lar) | Yıl | Başlık | Durum | Alaka | Notlar |
    |---|-----------|-----|--------|-------|-------|--------|
    | 1 | Smith, J | 2020 | Test Paper One | 🟢 Tamamlandı | ⭐⭐⭐ | paper1.pdf |
    | 2 | Jones, A | 2021 | Test Paper Two | 🔵 Havuzda | | paper2.pdf |
    | 3 | Brown, B | 2019 | Test Paper Three | 🔴 Ertelendi | | paper3.pdf |

    ## Notlar
""")

MINIMAL_STATUS = textwrap.dedent("""\
    # STATUS.md

    ```yaml
    document_type: thesis
    current_phase: 2
    sources:
      total_collected: 3
      read: 1
      deferred: 1
      saturation_reached: false
    ```
""")


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "READING_REPORT.md").write_text(MINIMAL_REPORT, encoding="utf-8")
    (tmp_path / "STATUS.md").write_text(MINIMAL_STATUS, encoding="utf-8")
    (tmp_path / "sources").mkdir()
    return tmp_path


# ── _parse_table ──────────────────────────────────────────────────────────────

class TestParseTable:
    def test_parses_row_count(self, project: Path) -> None:
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert len(rows) == 3

    def test_parses_row_n(self, project: Path) -> None:
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert rows[0]["n"] == 1
        assert rows[1]["n"] == 2

    def test_parses_status(self, project: Path) -> None:
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert STATUS_DONE in rows[0]["status"]
        assert STATUS_POOL in rows[1]["status"]
        assert STATUS_DEFERRED in rows[2]["status"]

    def test_parses_author(self, project: Path) -> None:
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert "Smith" in rows[0]["author"]

    def test_empty_content_returns_no_rows(self) -> None:
        _, rows, _ = _parse_table("")
        assert rows == []

    def test_before_and_after_preserved(self, project: Path) -> None:
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        before, _, after = _parse_table(content)
        assert any("READING_REPORT" in "".join(before) for _ in [1])
        assert any("Notlar" in "".join(after) for _ in [1])


# ── _write_report roundtrip ───────────────────────────────────────────────────

class TestWriteReport:
    def test_roundtrip_preserves_row_count(self, project: Path) -> None:
        path = project / "READING_REPORT.md"
        content = path.read_text(encoding="utf-8")
        before, rows, after = _parse_table(content)
        _write_report(path, before, rows, after)
        content2 = path.read_text(encoding="utf-8")
        _, rows2, _ = _parse_table(content2)
        assert len(rows2) == len(rows)

    def test_roundtrip_preserves_status(self, project: Path) -> None:
        path = project / "READING_REPORT.md"
        content = path.read_text(encoding="utf-8")
        before, rows, after = _parse_table(content)
        _write_report(path, before, rows, after)
        _, rows2, _ = _parse_table(path.read_text(encoding="utf-8"))
        for orig, new in zip(rows, rows2):
            assert orig["status"] == new["status"]


# ── cmd_sync ─────────────────────────────────────────────────────────────────

class TestCmdSync:
    def test_adds_new_pdfs(self, project: Path) -> None:
        (project / "sources" / "new_paper.pdf").write_bytes(b"%PDF")
        cmd_sync(project)
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        titles = [r["title"] for r in rows]
        assert any("new_paper" in t for t in titles)

    def test_does_not_duplicate_existing(self, project: Path) -> None:
        # paper1.pdf is already in notes column of row 1
        (project / "sources" / "paper1.pdf").write_bytes(b"%PDF")
        cmd_sync(project)
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        # Should still be 3 rows (no duplicate)
        assert len(rows) == 3

    def test_sync_with_no_pdfs(self, project: Path, capsys) -> None:
        cmd_sync(project)
        captured = capsys.readouterr()
        assert "bulunamadı" in captured.out or "bulunamadı" in captured.err or "yok" in captured.out

    def test_updates_status_md_total(self, project: Path) -> None:
        (project / "sources" / "extra.pdf").write_bytes(b"%PDF")
        cmd_sync(project)
        from core.session import TezAtlasSession
        state = TezAtlasSession(project).load()
        assert int((state.get("sources") or {}).get("total_collected", 0)) == 4

    def test_new_sources_get_pool_status(self, project: Path) -> None:
        (project / "sources" / "brandnew.pdf").write_bytes(b"%PDF")
        cmd_sync(project)
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        new_row = next(r for r in rows if "brandnew" in r["title"] or "brandnew" in r["notlar"])
        assert STATUS_POOL in new_row["status"]


# ── cmd_mark ─────────────────────────────────────────────────────────────────

class TestCmdMark:
    def test_mark_as_done(self, project: Path) -> None:
        cmd_mark(project, 2, "read")
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert STATUS_DONE in rows[1]["status"]

    def test_mark_as_deferred(self, project: Path) -> None:
        cmd_mark(project, 2, "defer")
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert STATUS_DEFERRED in rows[1]["status"]

    def test_mark_as_pool(self, project: Path) -> None:
        # Row 1 is currently done; reset to pool
        cmd_mark(project, 1, "pool")
        content = (project / "READING_REPORT.md").read_text(encoding="utf-8")
        _, rows, _ = _parse_table(content)
        assert STATUS_POOL in rows[0]["status"]

    def test_mark_syncs_status_md(self, project: Path) -> None:
        # Mark row 2 as done (total done: 2)
        cmd_mark(project, 2, "read")
        from core.session import TezAtlasSession
        state = TezAtlasSession(project).load()
        read_count = int((state.get("sources") or {}).get("read", 0))
        assert read_count == 2

    def test_mark_invalid_n_exits(self, project: Path) -> None:
        with pytest.raises(SystemExit):
            cmd_mark(project, 999, "read")

    def test_mark_saturation_detected(self, project: Path) -> None:
        # Mark all 3 rows as done → saturation should be reached
        cmd_mark(project, 1, "read")
        cmd_mark(project, 2, "read")
        cmd_mark(project, 3, "read")
        from core.session import TezAtlasSession
        state = TezAtlasSession(project).load()
        assert (state.get("sources") or {}).get("saturation_reached") is True
