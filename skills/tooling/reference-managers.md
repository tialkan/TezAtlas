---
title: "Reference Manager Integration (Zotero/Mendeley)"
title_tr: "Referans Yöneticisi Entegrasyonu (Zotero/Mendeley)"
node_type: tooling
priority: medium
description: "Guidelines and workflows for bridging TezAtlas with external reference managers via BibTeX/RIS export and import protocols."
description_tr: "BibTeX/RIS dışa ve içe aktarım protokolleri aracılığıyla TezAtlas'ı harici referans yöneticileriyle köprülemek için kılavuzlar ve iş akışları."
tags: [tooling, zotero, mendeley, bibtex, reference-management]
links_to:
  - skills/tooling/citation-formats.md
  - skills/core/iron-rules.md
language: bilingual
version: "1.0"
---

# Reference Manager Integration / Referans Yöneticisi Entegrasyonu

## Purpose / Amaç

**EN:** While TezAtlas handles citation formatting internally, researchers often have years of accumulated literature in Zotero, Mendeley, or EndNote. This node defines how to bridge external reference managers with the TezAtlas `/sources/` folder and `bibliography.md`.
**TR:** TezAtlas atıf biçimlendirmesini dahili olarak ele alırken, araştırmacılar genellikle Zotero, Mendeley veya EndNote'ta yıllarca birikmiş literatüre sahiptir. Bu node, harici referans yöneticilerini TezAtlas `/sources/` klasörü ve `bibliography.md` ile nasıl köprüleyeceğinizi tanımlar.

---

## 1. Importing Sources from Zotero (Phase 1/2) / Zotero'dan Kaynakları İçe Aktarma

**EN:** The strict Iron Rule 1 dictates that physical files must exist in the `/sources/` directory.

**Workflow:**
1.  In Zotero, select the papers for your project.
2.  Export the PDFs to the local TezAtlas `/sources/` folder.
3.  Right-click the same selection in Zotero and select **Export Items > BibTeX** (or BetterBibTeX).
4.  Save the file as `sources/references.bib`.
5.  *AI Action:* TezAtlas can parse `references.bib` to automatically understand the metadata (Author, Year, Journal) of all PDFs in the folder without relying solely on OCR.

## 2. Exporting TezAtlas Data to Zotero (Phase 7) / TezAtlas Verilerini Zotero'ya Dışa Aktarma

**EN:** After a project is finished, the researcher may want to save the new sources they found via Snowball Sampling (Phase 3) back to their main Zotero library.

**Workflow:**
1.  *User Command:* "Generate a RIS/BibTeX file of all sources used in this project."
2.  *AI Action:* The AI runs the verified generator, never writing metadata from memory: `python3 tools/bibtex_generator.py sources/ --output export.bib` (or `--format ris`). Entries marked `DOĞRULANMADI` or `verify manually` are listed for the user to check before import. If `sources/references.bib` from Zotero already exists, that file is the source of truth and is exported as is.
3.  The user can then drag and drop this file into Zotero to import the records.

## 3. Citation Key Standards / Atıf Anahtarı Standartları

**EN:** For users writing in LaTeX or using Pandoc, the AI must enforce a consistent citation key format across the project.
*   **Format:** `[AuthorLastname][Year][FirstWordOfTitle]` (e.g., `smith2023impact`).
*   **AI Prompting Rule:** When referencing a paper in the `Draft Generator` mode for a LaTeX/Pandoc project, always use `\cite{smith2023impact}` or `[@smith2023impact]` instead of plain text like "(Smith, 2023)".

## 4. Dealing with Missing Metadata / Eksik Meta Verilerle Başa Çıkma

**EN:** If the AI detects a PDF in `/sources/` that does not have a corresponding entry in `references.bib` or cannot be easily parsed for metadata:
*   *AI Action:* Intercept the workflow and ask the user for the DOI.
*   *AI Prompt:* "I see `new_paper.pdf` in the sources folder, but I don't have its metadata. Can you provide the DOI so I can format its citations correctly?"