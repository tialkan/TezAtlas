---
title: "Context Management — Session Memory System"
title_tr: "Context Yönetimi — Oturum Bellek Sistemi"
node_type: foundation
description: "Solves the blank-context problem across long thesis projects. Six files read at session start give complete project awareness even in session 50. Covers session rituals and long-gap recovery."
description_tr: "Uzun tez projelerinde boş-context sorununu çözer. Oturum başında okunan 6 dosya, 50. oturumda bile tam proje farkındalığı sağlar. Oturum ritüellerini ve uzun aranın ardından recovery'yi kapsar."
tags: [context-management, session-memory, recovery, foundation, always-active, six-files]
links_to:
  - skills/techniques/session-structure.md
  - skills/templates/tpl-status-summary.md
  - skills/templates/tpl-lessons.md
  - skills/templates/tpl-terminology.md
used_by:
  - skills/moc/MOC-core.md
  - skills/phases/thesis/phase-5-protocol.md
  - .claude/commands/tezatlas.md
language: bilingual
version: "2.1"
---

# Context Yönetimi / Context Management

## Problem

Uzun bir tez projesi onlarca oturum gerektirir. Her oturum başında AI'ın context'i sıfırdır. Bilgi kaybını önlemek için dosya tabanlı aktarım sistemi kullanılır.

A long thesis project requires dozens of sessions. Every session starts with a clean context. A file-based transfer system prevents knowledge loss.

## Oturum Başında Okunan 6 Dosya

Bu 6 dosya okunduğunda AI, projenin tam durumunu bilir — 50. oturumda bile.

```
1. CLAUDE.md          ← otomatik yüklenir (kısa özet, projenin anayasası özeti)
2. tezprotokol.md     ← projenin anayasası (Faz 5'te üretilir)
3. MEMORY.md          ← ilerleme durumu, sayısal veriler
4. DERSLER.md         ← birikmiş dersler (danışman + kullanıcı düzeltmeleri)
5. TERMINOLOJI.md     ← terim tutarlılığı sözlüğü
6. İlgili _notlar.md  ← yazılacak bölümün kaynak notları
```

Tam oturum ritüeli için [[session-structure]] düğümüne bak.

## Oturum Sonunda Güncellenen Dosyalar

```
1. MEMORY.md          ← SAYISAL veriler: kelime sayısı, son dipnot no, tamamlanan bölüm sayısı
2. DURUM_OZETI.md     ← NARRATİF durum: ne yapıldı, ne bekliyor, sonraki adım (şablon: [[tpl-status-summary]])
3. DERSLER.md         ← varsa yeni dersler (şablon: [[tpl-lessons]])
4. TERMINOLOJI.md     ← varsa yeni terimler (şablon: [[tpl-terminology]])
5. git commit         ← ZORUNLU — bkz. [[iron-rules]] Kural 6
```

## Oturum Sınırı Kararları

| Durum | Eylem |
|-------|-------|
| Alt bölüm tamamlandı | Kaydet → güncelle → yeni oturum |
| Alt bölüm yarım kaldı | `[DEVAM EDECEK]` etiketi → kaydet → yeni oturum |
| Context doluyor | Paragrafta dur → kaydet → yeni oturum |
| Uzun ara (günler/haftalar) | DURUM_OZETI.md oku → tam recovery |

## Uzun Ara Sonrası Recovery

Aylar sonra bile AI şunları okur ve tam durumu bilir:
1. `DURUM_OZETI.md` — en son ne yapıldı, ne bekliyor
2. `MEMORY.md` — sayısal ilerleme
3. `DERSLER.md` — birikmiş kurallar
4. Son yazılan bölümün son paragrafı — devamlılık

## Öz-İyileştirme Döngüsü (DERSLER.md)

Kullanıcı veya danışmandan gelen **her düzeltme** DERSLER.md'ye yazılır. Aynı hata iki kez tekrarlanmaz. Her oturum başında DERSLER.md okunur. Kurallar zaman içinde birikir — AI projeye özgü deneyim kazanır.

## MEMORY.md vs DURUM_OZETI.md — Fark

| Dosya | Rol | Format | Okuma Amacı |
|-------|-----|--------|-------------|
| `MEMORY.md` | Sayısal ilerleme sayaçları | Makine-okunabilir, kısa | "Kaçıncı dipnottayız? Kaç kelime yazıldı?" |
| `DURUM_OZETI.md` | Narrative durum raporu | İnsan-okunabilir, prose | "Aylar sonra nerede kalmıştık?" |

İkisini karıştırma: MEMORY.md'ye prose yazma, DURUM_OZETI.md'ye sayı gömme.
