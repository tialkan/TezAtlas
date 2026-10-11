---
title: "Source Hunting — Finding and Downloading Sources"
title_tr: "Kaynak Avcılığı — Kaynakları Bulma ve İndirme"
node_type: technique
description: "Four-channel source search strategy used in Phase 2 and triggered during Phases 3 and 6. Covers channel priority order, filename standardization, and the download chain."
description_tr: "Faz 2'de kullanılan ve Faz 3 ile 6'da tetiklenen dört kanallı kaynak arama stratejisi. Kanal öncelik sırası, dosya adı standardizasyonu ve indirme zincirini kapsar."
tags: [source-hunting, download, open-access, filename, phase-2, phase-3, phase-6]
links_to:
  - skills/tooling/open-access-chain.md
  - skills/core/iron-rules.md
  - skills/core/source-policy.md
used_by:
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-3-reading.md
  - skills/phases/thesis/phase-6-writing.md
  - skills/techniques/snowball-sampling.md
language: bilingual
version: "2.0"
---

# Kaynak Avcılığı / Source Hunting

## Arama Kanalları (Öncelik Sırasıyla)

1. **Açık erişim zinciri** — Unpaywall, OpenAlex, CORE, DergiPark → [[open-access-chain]]
2. **Açık erişim veritabanları:** SSRN, arXiv, CORE, OpenAlex, Google Scholar
3. **Kurumsal web siteleri:** BIS, IMF, ECB, BDDK, TCMB, resmi kurumlar
4. **Üniversite kütüphanesi:** Kullanıcı aracılığıyla (kütüphane erişimi)

## İndirme Zinciri

```
Kaynak ihtiyacı doğar (Faz 2, 3 veya 6)
  ↓
/sources/'da aranır
  ├─ BULUNDU → okuma kuyruğuna ekle
  └─ BULUNAMADI →
       1. Açık erişim kopyası ara (scripts/find_source.py)
       2. Bulunduysa → indir → /sources/'a kaydet
       3. İndirme başarısızsa → kullanıcıya tarayıcı linki ver
       4. Kaynak /sources/'a eklenince → kullanılabilir
```

## Dosya Adı Standardı

```
Bireysel eser:   Yazar_Yıl_Kısa_Başlık.pdf
Kurumsal rapor:  Kurum_Yıl_Kısa_Başlık.pdf
Çok yazarlı:     Yazar1_Yazar2_Yıl_Kısa_Başlık.pdf

Örnekler:
  Huber_2023_Monetary_Turning_Point.pdf
  BIS_2020_CBDC_Foundational_Principles.pdf
  Auer_Bohme_2020_Technology_Retail_CBDC.pdf
```

## Kullanıcıya Bildirim Formatı

Kaynağı indiremediğinde standart mesaj:
```
"Şu kaynak gerekli: [Yazar, Yıl, Başlık]
 İndirme linki: [url]
 Önerilen dosya adı: Yazar_Yıl_Kısa_Başlık.pdf
 Lütfen indirip /sources/ klasörüne kaydedin."
```

[[iron-rules]] Kural 3: AI önce kendisi indirir. İndiremezse o zaman kullanıcıya sorar.
