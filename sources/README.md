# sources/

Place your source PDFs here.

This directory is gitignored — its contents are personal and project-specific.
They will not be committed to the TezAtlas repository.

Each researcher's sources are different. This directory is yours alone.

## How to add sources

Drop PDF files directly into this directory, then run the TezAtlas source
ingestion workflow to extract text and register them in your source inventory.

- Text-layer PDFs are processed with PyMuPDF (no setup required).
- Scanned / image-only PDFs are processed with Tesseract (`apt install tesseract-ocr`).

## Where to find sources

See `skills/tooling/database-access.md` for guidance on:
- Open-access repositories (arXiv, PubMed, SSRN, DOAJ, BASE, OpenDOAR)
- Institutional library access
- Interlibrary loan workflows
- Legal access routes: open access, institutional access, interlibrary loan (see `skills/tooling/open-access-chain.md`)
- Google Scholar snowball sampling procedure

## Iron Rule reminder

Iron Rule 3: AI downloads first. Before you read a source manually, TezAtlas
attempts to retrieve it via open-access channels. Only verified, ingested sources
may be cited in your draft.
