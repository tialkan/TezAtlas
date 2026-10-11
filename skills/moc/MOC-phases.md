---
title: "MOC — Phases Cluster"
title_tr: "MOC — Fazlar Kümesi"
node_type: moc
cluster: phases
description: "Navigation hub for all 8 thesis phases. Each phase node gates into the next. Phase 3 is a loop (read → critical evaluation → snowball) until saturation. Phase 4 uses [[argument-mapping]] to derive structure from notes."
description_tr: "8 tez fazının tamamı için navigasyon merkezi. Her faz bir sonrakine geçişi kilitler. Faz 3 döngüdür: oku → eleştirel değerlendir → kartopu örnekle → doygunluğa kadar. Faz 4 [[argument-mapping]] ile notlardan yapı çıkarır."
tags: [moc, phases, navigation, workflow, sequential, phase-gated]
cluster_nodes:
  - skills/phases/thesis/phase-0-identity.md
  - skills/phases/thesis/phase-1-topic.md
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-3-reading.md
  - skills/phases/thesis/phase-4-structure.md
  - skills/phases/thesis/phase-5-protocol.md
  - skills/phases/thesis/phase-6-writing.md
  - skills/phases/thesis/phase-7-finalization.md
used_by:
  - skills/INDEX.md
language: bilingual
version: "2.1"
---

# MOC — Fazlar Kümesi / Phases Cluster

Çalışma akışı faz-kilitlidir — [[phase-2-sources]] minimum kaynak sayısını doğrulamadan [[phase-3-reading]]'e girilmez; [[phase-4-structure]]'ın danışman onayı alınmadan [[phase-6-writing]]'e geçilmez. [[phase-3-reading]] özeldir: oku → [[critical-reading]] ile eleştirel değerlendir → [[snowball-sampling]] ile yeni kaynak keşfet → her 5 kaynakta [[saturation-check]] — döngü.

## Faz Zinciri

```
[phase-0-identity] → [phase-1-topic] → [phase-2-sources]
  → [phase-3-reading ↻] → [phase-4-structure] → [phase-5-protocol]
  → [phase-6-writing] → [phase-7-finalization]
```

## Node'lar

| Faz | Amaç | Çıktı | Wikilink |
|-----|------|-------|----------|
| Faz 0 | Kimlik toplama | proje_kimlik.md | [[phase-0-identity]] |
| Faz 1 | Konu keşfi ve başlık | konu_kesfi.md | [[phase-1-topic]] |
| Faz 2 | Çekirdek kaynak avı | KAYNAK_ENVANTERI.md | [[phase-2-sources]] |
| Faz 3 | Okuma + kartopu (DÖNGÜ) | _notlar.md, OKUMA_RAPORU.md | [[phase-3-reading]] |
| Faz 4 | Yapı tasarımı | yapi_taslagi.md, SOURCE_MAP.md | [[phase-4-structure]] |
| Faz 5 | Protokol üretimi | tezprotokol.md, CLAUDE.md, bellek dosyaları | [[phase-5-protocol]] |
| Faz 6 | Oku ve yaz (DÖNGÜ) | Tez bölüm dosyaları | [[phase-6-writing]] |
| Faz 7 | Bitiriş ve savunma | KARSI_ARGUMANLAR.md, SAVUNMA_SORULARI.md | [[phase-7-finalization]] |
