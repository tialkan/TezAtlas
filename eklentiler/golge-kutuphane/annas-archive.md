---
title: "Anna's Archive — Source Download Integration"
title_tr: "Anna's Archive — Kaynak İndirme Entegrasyonu"
node_type: tooling
description: "Guide for using Anna's Archive via the annas_archive_helper.sh script. Covers search, download, quota check, and the full download chain from source need to /sources/ placement."
description_tr: "annas_archive_helper.sh scripti aracılığıyla Anna's Archive kullanım rehberi. Arama, indirme, kota kontrolü ve kaynak ihtiyacından /sources/ klasörüne yerleştirmeye kadar tam indirme zincirini kapsar."
tags: [tooling, annas-archive, download, script, source-hunting]
links_to:
  - skills/tooling/open-access-chain.md
language: bilingual
version: "2.0"
---

# Anna's Archive Entegrasyonu / Anna's Archive Integration

> **İsteğe bağlı eklenti.** Bu düğüm yalnız kullanıcı eklentiyi kendisi kurduğunda yüklenir. Önce her zaman yasal zincir denenir: [[open-access-chain]]. Bu sitelerin kullanımı birçok ülkede ve kurumda telif hukukuna ya da kurum politikasına aykırıdır; sorumluluk kullanıcıdadır.

## Script Kullanımı

```bash
# Arama
./scripts/annas_archive_helper.sh search "arama terimi"

# İndirme
./scripts/annas_archive_helper.sh download MD5_HASH dosya_adi.pdf

# Kota kontrolü
./scripts/annas_archive_helper.sh quota
```

**NOT:** Anna's Archive hesabı kullanıcıya aittir. API anahtarı scripte kullanıcı tarafından eklenir.

## İndirme Zinciri

[[iron-rules]] Kural 3 gereği AI önce kendisi indirir:

```
1. Kaynak ihtiyacı doğar (Faz 2, 3 veya 6)
2. /sources/ klasöründe ara
3. Bulunamazsa → Anna's Archive'da ara
4. Bulunduysa → script ile indir
5. İndirme başarılıysa → /sources/ klasörüne kaydet
6. İndirme başarısızsa → kullanıcıya tarayıcı linki ver
7. Kaynak /sources/'a eklenince → kullanılabilir, atıf yapılabilir
```

## Alternatif Kanallar (Anna's Archive başarısız olursa)

Tam fallback zinciri ve veritabanı rehberi için: [[database-access]]

Kısa özet (sırayla dene):
1. SSRN — Sosyal bilimler ve hukuk çalışma kağıtları
2. arXiv — Fizik, matematik, CS, ekonometri
3. CORE (core.ac.uk) — Genel açık erişim
4. ResearchGate / Academia.edu — Yazarın yüklediği versiyon
5. Unpaywall — Legal açık erişim versiyonu (DOI ile)
6. Kurumsal veritabanı (JSTOR, Scopus, LexisNexis) — VPN gerekebilir
7. Kullanıcıya sor: üniversite kütüphanesi VPN ile

## Kaynak Bulunamadığında

Kullanıcıya standart mesaj ([[source-hunting]] formatı):
```
"Şu kaynak Anna's Archive'da bulunamadı: [künye]
 Alternatif link: [varsa]
 Üniversite kütüphanenizde arayabilir misiniz?
 Önerilen dosya adı: Yazar_Yıl_Kısa_Başlık.pdf"
```
