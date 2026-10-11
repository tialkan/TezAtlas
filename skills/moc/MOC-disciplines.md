---
title: "MOC — Disciplines Cluster"
title_tr: "MOC — Disiplinler Kümesi"
node_type: moc
cluster: disciplines
description: "Navigation hub for 8 discipline-specific modules. Load exactly one discipline node at project start based on the student's field. Each module defines methodology, source hierarchy, citation default, and thesis structure."
description_tr: "8 disipline özgü modül için navigasyon merkezi. Proje başlangıcında öğrencinin alanına göre tam olarak bir disiplin node'u yükle. Her modül metodoloji, kaynak hiyerarşisi, varsayılan atıf sistemi ve tez yapısını tanımlar."
tags: [moc, disciplines, navigation, methodology, citation-default]
cluster_nodes:
  - templates/disciplines/hukuk.md
  - templates/disciplines/sosyal-bilimler.md
  - templates/disciplines/muhendislik.md
  - templates/disciplines/fen-bilimleri.md
  - templates/disciplines/tip.md
  - templates/disciplines/isletme.md
  - templates/disciplines/egitim.md
  - templates/disciplines/beseri-bilimler.md
used_by:
  - skills/INDEX.md
  - skills/phases/thesis/phase-0-identity.md
language: bilingual
version: "2.0"
---

# MOC — Disiplinler Kümesi / Disciplines Cluster

[[phase-0-identity]]'de disiplin belirlenir ve tam olarak bir disiplin node'u yüklenir — hukuk öğrencisi için [[law]], tıp öğrencisi için [[medicine]]. Her disiplin node'u [[MOC-citations]]'a çapraz referans verir ve varsayılan atıf sistemini otomatik belirler.

## Disiplin → Atıf Sistemi Varsayılanları

| Disiplin | Varsayılan Atıf | Alternatif | Wikilink |
|----------|----------------|------------|----------|
| Hukuk | Chicago Notes-Bibliography | OSCOLA | [[law]] |
| Sosyal Bilimler | APA 7 | Chicago Author-Date | [[social-sciences]] |
| Mühendislik | IEEE | APA | [[stem]] |
| Fen Bilimleri | APA | IEEE | [[stem]] |
| Tıp | Vancouver | APA | [[medicine]] |
| İşletme | APA | Harvard | [[isletme]] |
| Eğitim | APA 7 | Chicago | [[egitim]] |
| Beşeri Bilimler | Chicago Notes-Bibliography | Harvard | [[humanities]] |

Her disiplin node'u ayrıca şunları içerir: metodoloji gereksinimleri, yazım kuralları, kaynak kalite hiyerarşisi, tez yapı önerileri, sık yapılan hatalar.
