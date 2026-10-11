"""
test_ocr_pipeline.py — OCR pipeline functional tests.

Tests:
1. Module imports correctly
2. Text-layer PDF extraction (using a generated minimal PDF)
3. Batch mode returns expected structure
4. CLI help text available
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
OCR_SCRIPT = REPO_ROOT / "ocr_pipeline.py"


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def minimal_pdf(tmp_path_factory):
    """
    Create a minimal PDF with text layer for testing.
    Uses PyMuPDF (fitz) to create it — so if fitz isn't installed,
    this fixture is skipped.
    """
    fitz = pytest.importorskip("fitz", reason="PyMuPDF required for OCR tests")
    tmp = tmp_path_factory.mktemp("pdfs")
    pdf_path = tmp / "test_document.pdf"
    doc = fitz.open()
    page = doc.new_page()
    # Text must exceed 100 chars/page threshold for PyMuPDF text-layer detection
    text = (
        "TezAtlas OCR Test Document\n\n"
        "This document tests the PyMuPDF text layer extraction pipeline.\n"
        "Academic content: Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
        "Research methods, data analysis, and citation verification are core features.\n"
        "Source: TezAtlas Test Suite (2024). Page 1."
    )
    page.insert_text((50, 100), text, fontsize=11)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


# ──────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────

class TestOCRPipelineImport:
    def test_script_exists(self):
        assert OCR_SCRIPT.exists(), f"ocr_pipeline.py not found at {OCR_SCRIPT}"

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, str(OCR_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()


class TestTextLayerExtraction:
    def test_extract_text_from_pdf(self, minimal_pdf):
        """PyMuPDF text extraction returns non-empty text."""
        fitz = pytest.importorskip("fitz")
        doc = fitz.open(str(minimal_pdf))
        page = doc[0]
        text = page.get_text()
        doc.close()
        assert "TezAtlas" in text
        assert len(text) > 10

    def test_ocr_pipeline_single_file(self, minimal_pdf, tmp_path):
        """ocr_pipeline.py processes a single PDF and returns JSON output."""
        out_file = tmp_path / "result.json"
        result = subprocess.run(
            [sys.executable, str(OCR_SCRIPT), str(minimal_pdf), "--output", str(out_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"OCR pipeline failed: {result.stderr}"
        assert out_file.exists(), "No output file created"
        data = json.loads(out_file.read_text())
        assert isinstance(data, (dict, list)), "Output should be JSON object or array"


class TestBatchMode:
    def test_batch_mode_empty_dir(self, tmp_path):
        """Batch mode on empty directory exits without error."""
        result = subprocess.run(
            [sys.executable, str(OCR_SCRIPT), str(tmp_path), "--batch"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        # Should exit 0 even if no PDFs found
        assert result.returncode == 0

    def test_batch_mode_with_pdfs(self, minimal_pdf, tmp_path):
        """Batch mode processes PDFs in a directory."""
        import shutil
        # Copy test PDF to tmp_path
        dest = tmp_path / "sample.pdf"
        shutil.copy(str(minimal_pdf), str(dest))
        result = subprocess.run(
            [sys.executable, str(OCR_SCRIPT), str(tmp_path), "--batch"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Batch mode failed: {result.stderr}"
