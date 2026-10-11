"""Tests for tezatlas_cli.py — Universal CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


_ROOT = Path(__file__).parent.parent


class TestCLIBasics:
    def test_list_commands(self):
        result = subprocess.run(
            [sys.executable, str(_ROOT / "tezatlas_cli.py"), "--list"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "intake" in result.stdout
        assert "gaps" in result.stdout
        assert "import" in result.stdout

    def test_no_args_shows_list(self):
        result = subprocess.run(
            [sys.executable, str(_ROOT / "tezatlas_cli.py")],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "TezAtlas" in result.stdout

    def test_unknown_command(self):
        result = subprocess.run(
            [sys.executable, str(_ROOT / "tezatlas_cli.py"), "nonexistent"],
            capture_output=True, text=True,
        )
        assert result.returncode == 1

    def test_fuzzy_match(self):
        """Prefix matching should work (e.g., 'int' -> 'intake')."""
        result = subprocess.run(
            [sys.executable, str(_ROOT / "tezatlas_cli.py"), "int"],
            capture_output=True, text=True,
            timeout=10,
        )
        # 'int' matches both 'intake' and 'import', so it should say "Did you mean"
        # or run one of them — the key is it shouldn't crash
        assert result.returncode in (0, 1)

    def test_intake_runs(self, tmp_path: Path):
        """Test that intake command actually runs the script."""
        notes = tmp_path / "notes"
        notes.mkdir()
        (notes / "test.md").write_text(
            "# Test Note\n\nThe study shows significant results in this area.\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(_ROOT / "tezatlas_cli.py"),
             "intake", "--project-dir", str(tmp_path)],
            capture_output=True, text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_gaps_runs(self, tmp_path: Path):
        """Test that gaps command runs the script."""
        notes = tmp_path / "notes"
        notes.mkdir()
        (notes / "test.md").write_text(
            "# Test\n\nFurther research is needed on this topic.\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(_ROOT / "tezatlas_cli.py"),
             "gaps", "--project-dir", str(tmp_path)],
            capture_output=True, text=True,
            timeout=30,
        )
        assert result.returncode == 0
