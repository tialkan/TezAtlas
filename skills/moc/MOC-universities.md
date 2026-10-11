---
title: "MOC — Universities Cluster"
title_tr: "MOC — Üniversiteler Kümesi"
node_type: moc
cluster: universities
description: "Navigation hub for university formatting YAML templates. Load the matching template once during Phase 0 to configure margins, fonts, line spacing, and front-matter page order."
description_tr: "Üniversite format YAML şablonları için navigasyon merkezi. Kenar boşlukları, yazı tipi, satır aralığı ve ön matter sayfa düzenini yapılandırmak için Faz 0 sırasında eşleşen şablonu bir kez yükle."
tags: [moc, universities, formatting, yaml, navigation]
cluster_nodes:
  - templates/universities/odtu.yaml
  - templates/universities/itu.yaml
  - templates/universities/bogazici.yaml
  - templates/universities/hacettepe.yaml
  - templates/universities/ankara.yaml
  - templates/universities/asbu.yaml
  - templates/universities/ornek.yaml
used_by:
  - skills/INDEX.md
  - skills/phases/thesis/phase-0-identity.md
language: bilingual
version: "2.0"
---

# MOC — Üniversiteler Kümesi / Universities Cluster

Üniversite şablonları [[phase-0-identity]] sırasında bir kez yüklenir. Öğrencinin üniversitesi listede yoksa [[university-template-blank]] boş şablonu kullan ve üniversitenin tez yazım kılavuzunu öğrenciden iste.

## Desteklenen Üniversiteler

| Üniversite | Kısaltma | Odak | YAML |
|------------|----------|------|------|
| Orta Doğu Teknik Üniversitesi | ODTÜ | Mühendislik, Fen | `templates/universities/odtu.yaml` |
| İstanbul Teknik Üniversitesi | İTÜ | Mühendislik | `templates/universities/itu.yaml` |
| Boğaziçi Üniversitesi | BOUN | Sosyal Bilimler | `templates/universities/bogazici.yaml` |
| Hacettepe Üniversitesi | HÜ | Sağlık Bilimleri | `templates/universities/hacettepe.yaml` |
| Ankara Üniversitesi | AÜ | Hukuk, Genel | `templates/universities/ankara.yaml` |
| Ankara Sosyal Bilimler Üni. | ASBÜ | Sosyal Bilimler, Hukuk | `templates/universities/asbu.yaml` |
| Örnek/Boş Şablon | — | Yeni üniversite eklemek için | `templates/universities/ornek.yaml` |

Her YAML şablonu şunları içerir: kenar boşlukları, yazı tipi ve boyutu, satır aralığı, paragraf girintisi, başlık formatları, dipnot boyutu, kaynakça düzeni, intihal araç gereksinimleri.
