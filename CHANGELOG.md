# Changelog

All notable changes to TezAtlas are documented in this file.

---

## [1.2.0] — 2026-10-12

### Uydurma ve yanlış künye riskine karşı
- `tools/bibtex_generator.py`: PDF'te bulunan bir DOI'nin künyesi artık yalnız Crossref başlığı PDF'in ilk sayfalarında geçiyorsa kabul ediliyor. İlk sayfalardaki başka eserlere ait DOI'ler reddediliyor; OpenAlex başlık aramasında da aynı denetim var. Eşleşme yoksa giriş `@misc` olarak, reddedilen adaylar `% DOĞRULANMADI` notuyla yazılıyor.
- BibTeX alanlarında LaTeX özel karakterleri kaçışlanıyor, atıf anahtarları ASCII ve tekil (`Smith2020a`).
- Kaynak avcısı ajanı: modelin her önerisi Crossref ile karşılaştırılıyor (DOI başka bir esere aitse ya da kayıt bulunamazsa öneri `unverified` listesine ayrılıyor). Yeni modül: `agents/core/kaynak_dogrulama.py`.
- `reference-managers.md` dışa aktarımı doğrulanmış üreticiye bağlandı; `publication-strategist.md` hafızadan etki faktörü vermiyor.

### Düzeltmeler
- MCP sunucusu güncel `mcp` 1.x ile açılıyor (önceden hiçbir sürümde çalışmıyordu); araçlar olay döngüsünü kilitlemiyor. Duman testi eklendi.
- Akademik API istemcisi 429 ve geçici sunucu hatalarında `Retry-After`'a uyarak yeniden deniyor; hata olursa "sonuç yok" yerine hatayı bildiriyor.
- `scripts/find_source.py --llm-enhance` hiç çalışmıyordu (var olmayan argümanlar); düzeltildi ve yalnız doğrulanmış önerileri ek sorgu olarak kullanıyor.
- Çelişen mod tanımı (`core/modes.md`) kaldırıldı, kanonik düğüme yönlendirildi; eksik `/mode` komutu eklendi.

---

## [1.1.0] — 2026-10-11

Ayrıntılı gerekçe: `docs/inceleme-2026.md`.

### Güvenlik
- Kişisel `.claude/settings.local.json` repodan çıkarıldı ve `.gitignore`'a eklendi.

### Düzeltmeler
- `pip install -e .` çalışmıyordu (`build-backend` hatası); `core` paketi, `tezatlas_cli` ve `ocr_pipeline` pakete eklendi. Yeni `tezatlas` komutu.
- Hibe ve araştırma önerisi türleri var olmayan dosyalara yönleniyordu; poster ve teknik rapor türlerine ulaşılamıyordu. Onboarding tablosu düzeltildi, Türkçe bölüme de yönlendirme tablosu eklendi.
- 47 kırık `used_by` yolu düzeltildi. Yeni `scripts/check_links.py` CI'da her değişiklikte çalışır.
- `RESEARCH_BACKING.md`: var olmayan bir künye (Pychyl & Flett 2012) ve hatalı künyeler (Lovitts 2001, Wisker 2005, Flower & Hayes 1981) düzeltildi; DOI'ler eklendi.
- ruff ile bulunan ölü kod ve kullanılmayan değişkenler temizlendi.

### Değişiklikler
- Kaynak edinme zinciri yalnız yasal kanallardan oluşuyor (`skills/tooling/open-access-chain.md`). Anna's Archive düğümü isteğe bağlı `eklentiler/golge-kutuphane/` eklentisine taşındı.
- Çoklu model: OpenRouter sağlayıcısı eklendi; üç ajan varsayılan olarak farklı sağlayıcıların modellerine atandı. Model adları `.env` içinde `<SAĞLAYICI>_MODEL` ile değiştirilebiliyor. `timeout`, `max_retries` ve `max_tokens` artık gerçekten uygulanıyor; eksik API anahtarı anlaşılır bir mesajla bildiriliyor; token kullanımı kaydediliyor.
- Crossref/OpenAlex iletişim adresi `TEZATLAS_MAILTO` ile ayarlanabiliyor.
- README Türkçe olarak yeniden yazıldı; İngilizce ayrıntılı belge `docs/README.en.md`'ye taşındı ve sayıları düzeltildi.
- Eski tanıtım sitesi (`website/`) kaldırıldı; canlı site ayrı repoda.
- CI tek işte birleşti: paket kurulumu, ruff, tüm testler, bağlantı denetimi.

---

### Mid-Project Import & Universal CLI

- **`/import` command** — Import existing academic work (PDFs, notes, drafts) and start at the detected phase. No need to redo earlier work.
  - `scripts/import_project.py` — Scans directory, classifies artifacts, detects appropriate phase
  - Auto-organizes scattered PDFs into `sources/`, notes into `notes/`
  - Phase override option for manual control
- **`tezatlas_cli.py` — Universal CLI** — Use TezAtlas from any terminal without Claude Code
  - `tezatlas intake`, `tezatlas gaps`, `tezatlas import`, etc.
  - Works with Cursor, Aider, Windsurf, or standalone
  - Fuzzy command matching, `--list` for full reference
- **26 new tests** (`test_import_project.py` + `test_cli.py`)
- **Total: 266 tests passing**

---

### Literature Intelligence Layer (Literatur Zekasi Katmani)

TezAtlas includes a comprehensive literature intelligence system with 8 new slash commands, a proactive literature alignment engine, and section-aware draft review.

#### New Slash Commands — 9 Academic Analysis Prompts

| Command | Script | Output | Purpose |
|---------|--------|--------|---------|
| `/intake` | `scripts/intake_protocol.py` | SOURCE_MAP.md | Source clustering + core claim extraction + conflict detection |
| `/contradictions` | `scripts/contradiction_scan.py` | CONTRADICTIONS.md | Enhanced cross-source contradiction analysis (now scans notes/ + ARGUMENTS.md + SYNTHESIS.md) |
| `/citation-chain` | `scripts/citation_chain.py` | CITATION_CHAIN.md | Intellectual lineage per concept: who started → challenged → developed → consensus |
| `/gaps` | `scripts/gap_scanner.py` | GAPS.md | Research gap detection: explicit gaps, open questions, argument coverage, methodology gaps |
| `/method-audit` | _(methodology_checker agent)_ | _(interactive)_ | Methodology audit across sources + user's own method validation |
| `/assumptions` | `scripts/assumption_killer.py` | ASSUMPTIONS.md | Untested shared assumption finder with risk analysis |
| `/knowledge-map` | `scripts/knowledge_map.py` | KNOWLEDGE_MAP.md | Field structure: support pillars + contention zones + boundary questions + essential reads |
| `/so-what` | `scripts/so_what_test.py` | SO_WHAT.md | "So What?" significance test: 3 essential statements (proven, unknown, impact) |

#### Literature Intelligence Engine

- **New module: `core/literature_intel.py`**
  - `NoteIndex` — keyword-based in-memory index of all notes for fast matching
  - `ArgumentIndex` — ARGUMENTS.md argument index with keyword matching
  - `LiteratureIntel` — paragraph-level source suggestions, contradiction warnings, argument alignment
  - `detect_section_type()` — auto-detects Intro/Literature/Method/Results/Discussion/Conclusion from filename + content

#### Section Infrastructure (Bolum Bazli Altyapi)

- **6 section types** with specialized tools and quality checks:
  - Intro → `/so-what`, `/knowledge-map` + RQ clarity, scope control
  - Literature → `/intake`, `/contradictions`, `/citation-chain`, `/gaps` + coverage sufficiency, bias check
  - Method → `/method-audit` + internal consistency, validity
  - Results → over-claiming control
  - Discussion → `/assumptions`, `/knowledge-map`, `/devil-advocate` + argument integrity, limitations
  - Conclusion → `/so-what`, `/synthesize` + generalization control, contribution clarity
- **New guide: `skills/core/section-infrastructure.md`**
- **New guide: `skills/core/literature-intelligence.md`**

#### Enhanced `/review-draft` — 4 Layers

| Layer | Name | Status |
|-------|------|--------|
| 1 | Argument Integrity | existing |
| 2 | Source Integrity | existing |
| 3 | Style & Language | existing |
| **4** | **Literature Alignment** | **NEW** |

Layer 4 adds: section type auto-detection, per-paragraph source matching, contradiction warnings, unsupported claim flags, and section-specific tool recommendations.

#### Enhanced `/contradictions`

- Now scans `notes/` + `ARGUMENTS.md` + `SYNTHESIS.md` (previously only notes/)
- New slash command file with structured contradiction categorization (real conflict / context difference / conceptual difference)

### Tests

- **67 new tests** across 4 test files
- `tests/test_intake_protocol.py` — 15 tests
- `tests/test_gap_scanner.py` — 10 tests
- `tests/test_literature_intel.py` — 22 tests
- `tests/test_new_commands.py` — 20 tests (so_what, knowledge_map, assumption_killer, citation_chain)
- **Total: 240 tests passing** (was 173)
- Zero regressions on existing tests

### Documentation

- `CLAUDE.md` updated with full slash command reference and section infrastructure docs
- `README.md` updated with Literature Intelligence section
- `CHANGELOG.md` created (this file)

---

### Initial Release

- Phase-gated academic workflow framework
- 9 Iron Rules enforcement
- 8 document types (thesis, article, conference paper, lit review, report, book chapter, grant proposal, research proposal)
- Multi-agent system (source_hunter, methodology_checker, citation_verifier)
- OCR pipeline (PyMuPDF + Tesseract)
- MCP server for academic APIs (Semantic Scholar, OpenAlex, CrossRef)
- Session management with STATUS.md and DASHBOARD.md
- Snowball sampling automation
- BibTeX/RIS generation from DOI
- Style linting (passive voice, hedging, over-claiming)
- Plugin system and TezAtlas Exchange
- Next.js marketing website
- 149 tests passing
