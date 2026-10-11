---
title: "MOC — Citations Cluster"
title_tr: "MOC — Atıf Sistemleri Kümesi"
node_type: moc
cluster: citations
description: "Navigation hub for 6 citation system reference guides. Load the relevant one during Phase 5 and keep it accessible during Phase 6 writing. Each guide contains complete formatting for all source types."
description_tr: "6 atıf sistemi rehberi için navigasyon merkezi. İlgili olanı Faz 5'te yükle ve Faz 6 yazımı boyunca erişilebilir tut. Her rehber tüm kaynak türleri için tam formatlama içerir."
tags: [moc, citations, navigation, formatting, reference]
cluster_nodes:
  - templates/citations/chicago-notes.md
  - templates/citations/apa7.md
  - templates/citations/harvard.md
  - templates/citations/ieee.md
  - templates/citations/oscola.md
  - templates/citations/vancouver.md
used_by:
  - skills/INDEX.md
  - skills/phases/thesis/phase-0-identity.md
  - skills/phases/thesis/phase-5-protocol.md
  - skills/phases/thesis/phase-6-writing.md
language: bilingual
version: "2.0"
---

# MOC — Atıf Sistemleri Kümesi / Citations Cluster

Atıf node'ları iş akışı node'ları değil referans belgelerdir — [[phase-5-protocol]] sırasında ilgili olanı yükle ve [[phase-6-writing]] boyunca erişilebilir tut. Hangi atıf sistemini seçeceğini bilmiyorsan [[MOC-disciplines]] disiplin-atıf eşleştirme tablosunu kullan.

## Atıf Sistemleri

| Sistem | Birincil Kullanım | Yapı | Wikilink |
|--------|------------------|------|----------|
| Chicago Notes-Bibliography | Hukuk, Beşeri Bilimler | Dipnot + Kaynakça | [[chicago-notes]] |
| APA 7 | Sosyal Bilimler, Eğitim, İşletme, Tıp | Metin içi (Yazar, Yıl) | [[apa7]] |
| Harvard | İşletme, Genel | Metin içi (Author Year) | [[harvard]] |
| IEEE | Mühendislik, Fen Bilimleri | Numaralı [1], [2], [3] | [[ieee]] |
| OSCOLA | İngiliz Hukuku | Dipnot | [[oscola]] |
| Vancouver | Tıp, Sağlık Bilimleri | Numaralı sürekli | [[vancouver]] |

**Not:** Mevzuat metinleri ve mahkeme kararları çoğu sistemde kaynakçaya dahil edilmez — yalnızca dipnotta verilir. Disipline özgü istisnalar için [[law]] modülüne bak.
