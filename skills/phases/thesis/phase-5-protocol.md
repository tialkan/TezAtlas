---
title: "Phase 5 — Protocol Generation"
title_tr: "Faz 5 — Protokol Üretimi"
node_type: phase
phase_number: 5
phase_gate_in: "phase-4-structure.md"
phase_gate_out: "phase-6-writing.md"
description: "Combine all Phase 0-4 information to generate project-specific files: tezprotokol.md (project constitution), CLAUDE.md (auto-loaded summary), and four memory files. Initialize git repository."
description_tr: "Faz 0-4'teki tüm bilgileri birleştirerek projeye özgü dosyaları üret: tezprotokol.md (proje anayasası), CLAUDE.md (otomatik yüklenen özet) ve dört bellek dosyası. Git deposunu başlat."
tags: [phase, protocol-generation, project-constitution, memory-files, git-init]
outputs:
  - tezprotokol.md
  - CLAUDE.md
  - MEMORY.md
  - DERSLER.md
  - TERMINOLOJI.md
  - DURUM_OZETI.md
links_to:
  - skills/core/context-management.md
  - skills/core/agent-orchestration.md
  - skills/tooling/git-workflow.md
  - skills/templates/tpl-status-summary.md
  - skills/templates/tpl-lessons.md
  - skills/templates/tpl-terminology.md
  - skills/templates/tpl-thesis-protocol.md
  - skills/moc/MOC-citations.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-4-structure.md
  - skills/phases/thesis/phase-6-writing.md
language: bilingual
version: "2.0"
---

# Faz 5 — Protokol Üretimi / Phase 5 — Protocol Generation

## Amaç

Faz 0-4'teki tüm bilgileri birleştirerek projeye özgü dosyalar üretmek. Bu dosyalar [[context-management]] sisteminin temelini oluşturur.

## Üretilen Dosyalar

**1. tezprotokol.md** — Projeye özel yazım protokolü:

Şablon: [[tpl-thesis-protocol]] — bu şablonu açarak aşağıdaki bilgileri doldur:

- Proje kimliği (Faz 0'dan — proje_kimlik.md)
- Tez başlığı, anahtar kavramlar, araştırma soruları (Faz 1'den — konu_kesfi.md)
- Tez yapısı ve dosya haritası (Faz 4'ten — yapi_taslagi.md)
- Kaynak politikası (evrensel kurallar + projeye özel istisnalar)
- Atıf sistemi detaylı format örnekleri ([[MOC-citations]]'dan)
- Yazım standartları (üniversite şablonundan)
- Bölüm bazlı uzunluk hedefleri
- Teorik çerçeve özeti (Faz 3 okumalarından)
- Kritik uyarılar (başlangıçta boş, DERSLER.md'den dolar)
- Oturum planı (6 dosya oku, 5 dosya güncelle)

**2. CLAUDE.md** — Her oturumda otomatik yüklenen kısa özet:
- Projenin ne olduğu (1 paragraf)
- Demir kurallar (5 madde)
- Kritik uyarılar
- Okunması gereken dosya listesi

**3. MEMORY.md** — İlerleme takibi (başlangıçta):
```
Tamamlanan bölümler: (boş)
Son dipnot no: 0
Toplam kelime: 0
Sonraki adım: Faz 6 başlangıcı
```

**4. DERSLER.md** — Öz-iyileştirme (başlangıçta boş, zamanla dolar) — şablon: [[tpl-lessons]]

**5. TERMINOLOJI.md** — Tutarlılık (Faz 1'deki anahtar kavramlarla başlar) — şablon: [[tpl-terminology]]

**6. DURUM_OZETI.md** — Her oturum sonunda güncellenen detaylı durum raporu — şablon: [[tpl-status-summary]]

## Git Başlatma

Detay [[git-workflow]]'da:
```bash
git init
git add .
git commit -m "TezAtlas: Proje kurulumu tamamlandı — Faz 0-5"
```
