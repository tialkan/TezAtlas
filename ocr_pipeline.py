#!/usr/bin/env python3
"""
TezAtlas OCR Pipeline
-----------------------
Extracts text from PDFs using:
  1. PyMuPDF  — text-layer extraction (fast, no OCR needed, works for ~80% of academic PDFs)
  2. Tesseract — fallback for scanned/image-only PDFs (apt install tesseract-ocr)

No GPU, no API key, no special hardware required.

Usage:
    python3 ocr_pipeline.py input.pdf                    # auto mode
    python3 ocr_pipeline.py input.pdf --output out.json  # save to JSON
    python3 ocr_pipeline.py sources/ --batch             # process whole folder
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("[WARNING] PyMuPDF not installed. Run: pip install pymupdf", file=sys.stderr)

try:
    import pytesseract
    from PIL import Image
    import io
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def has_text_layer(pdf_path: str, sample_pages: int = 5) -> bool:
    """Check if PDF has a text layer (not scanned)."""
    if not PYMUPDF_AVAILABLE:
        return False
    doc = fitz.open(pdf_path)
    pages_to_check = min(sample_pages, len(doc))
    total_chars = 0
    for i in range(pages_to_check):
        text = doc[i].get_text()
        total_chars += len(text.strip())
    doc.close()
    return total_chars > 100 * pages_to_check  # >100 chars/page = has text layer


def extract_with_pymupdf(pdf_path: str) -> list[dict]:
    """Extract text using PyMuPDF (text-layer PDFs)."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page": i + 1,
            "text": text.strip(),
            "method": "pymupdf"
        })
    doc.close()
    return pages


def extract_with_tesseract(pdf_path: str, lang: str = "tur+eng") -> list[dict]:
    """Extract text using Tesseract OCR (scanned PDFs)."""
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF required for page-to-image conversion. pip install pymupdf")
    if not TESSERACT_AVAILABLE:
        raise RuntimeError("Tesseract not available. pip install pytesseract pillow && apt install tesseract-ocr")

    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR accuracy
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(img, lang=lang)
        pages.append({
            "page": i + 1,
            "text": text.strip(),
            "method": "tesseract"
        })
        print(f"  Page {i+1}/{len(doc)}", end="\r", file=sys.stderr)
    doc.close()
    print("", file=sys.stderr)
    return pages


def process_pdf(pdf_path: str, force_ocr: bool = False, lang: str = "tur+eng") -> dict:
    """Process a single PDF. Auto-detect method."""
    pdf_path = str(pdf_path)

    print(f"[TezAtlas OCR] {Path(pdf_path).name}", file=sys.stderr)

    if not force_ocr and has_text_layer(pdf_path):
        print("  → Text layer detected, using PyMuPDF", file=sys.stderr)
        pages = extract_with_pymupdf(pdf_path)
    else:
        print(f"  → Scanned PDF, using Tesseract (lang={lang})", file=sys.stderr)
        pages = extract_with_tesseract(pdf_path, lang=lang)

    return {
        "source": Path(pdf_path).name,
        "total_pages": len(pages),
        "method": pages[0]["method"] if pages else "none",
        "pages": pages
    }


def batch_process(folder: str, output_dir: str = "output", lang: str = "tur+eng"):
    """Process all PDFs in a folder."""
    folder = Path(folder)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pdfs = list(folder.glob("*.pdf"))
    print(f"[TezAtlas OCR] Found {len(pdfs)} PDFs in {folder}", file=sys.stderr)

    for i, pdf in enumerate(pdfs, 1):
        out_file = output_dir / (pdf.stem + ".json")
        if out_file.exists():
            print(f"  [{i}/{len(pdfs)}] Skipping (already done): {pdf.name}", file=sys.stderr)
            continue

        print(f"  [{i}/{len(pdfs)}] Processing: {pdf.name}", file=sys.stderr)
        try:
            result = process_pdf(str(pdf), lang=lang)
            out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"  [ERROR] {pdf.name}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="TezAtlas OCR Pipeline — PyMuPDF + Tesseract"
    )
    parser.add_argument("input", help="PDF file or folder (with --batch)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON file")
    parser.add_argument("--batch", action="store_true", help="Process entire folder")
    parser.add_argument("--ocr", action="store_true", help="Force Tesseract even if text layer exists")
    parser.add_argument("--lang", default="tur+eng", help="Tesseract language(s), e.g. tur+eng, eng, deu")
    parser.add_argument("--output-dir", default="output", help="Output folder for batch mode")
    args = parser.parse_args()

    if args.batch:
        batch_process(args.input, args.output_dir, args.lang)
    else:
        result = process_pdf(args.input, force_ocr=args.ocr, lang=args.lang)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            sys.stdout.buffer.write(output.encode("utf-8"))


if __name__ == "__main__":
    main()
