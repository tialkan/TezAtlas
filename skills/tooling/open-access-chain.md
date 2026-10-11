---
title: "Legal Source Acquisition Chain"
title_tr: "Yasal Kaynak Edinme Zinciri"
node_type: tooling
description: "Default order for obtaining a source PDF legally: open access discovery (Unpaywall, OpenAlex, CORE), repositories and preprints, Turkish national sources (DergiPark, YÖK Thesis Center), institutional access, interlibrary loan, and asking the author."
description_tr: "Bir kaynağın PDF'ini yasal yoldan edinmenin varsayılan sırası: açık erişim keşfi (Unpaywall, OpenAlex, CORE), kurumsal arşivler ve ön baskılar, ulusal kaynaklar (DergiPark, YÖK Ulusal Tez Merkezi), kurum erişimi, kütüphaneler arası ödünç ve yazardan isteme."
tags: [tooling, open-access, download, source-hunting, legal]
links_to:
  - skills/core/iron-rules.md
  - skills/techniques/source-hunting.md
  - skills/tooling/database-access.md
used_by:
  - skills/core/iron-rules.md
  - skills/core/source-policy.md
  - skills/core/working-principles.md
  - skills/core/error-recovery.md
  - skills/techniques/source-hunting.md
  - skills/techniques/snowball-sampling.md
  - skills/techniques/source-acquisition-protocol.md
  - skills/techniques/pdf-reading.md
  - skills/tooling/database-access.md
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-3-reading.md
  - skills/phases/thesis/phase-6-writing.md
language: bilingual
version: "1.0"
---

# Yasal Kaynak Edinme Zinciri / Legal Source Acquisition Chain

Demir Kural 3 gereği yapay zekâ, kaynağı kullanıcıdan istemeden önce kendisi bulmaya çalışır. Bunu aşağıdaki sırayla ve yalnız yasal kanallardan yapar. Her adımda ne denendiği `READING_REPORT.md` / `OKUMA_RAPORU.md` tablosuna yazılır.

## Sıra

1. **DOI ile açık erişim kopyası**
   - Unpaywall: `https://api.unpaywall.org/v2/<DOI>?email=<TEZATLAS_MAILTO>` → `best_oa_location.url_for_pdf`
   - OpenAlex: `https://api.openalex.org/works/doi:<DOI>` → `open_access.oa_url`
   - `scripts/find_source.py` bu iki adımı otomatik dener.
2. **Açık arşivler ve ön baskılar:** CORE (core.ac.uk), arXiv, SSRN, PubMed Central, Zenodo, OSF Preprints, yazarın üniversite arşivi. Ön baskı yayımlanmış sürümle aynı olmayabilir; kaynakçada hangi sürümün okunduğu belirtilir.
3. **Ulusal kaynaklar:** DergiPark (Türkçe dergi makalelerinin çoğu açık erişimli), YÖK Ulusal Tez Merkezi (izin verilmiş tezler), TÜBİTAK ULAKBİM TR Dizin kayıtları.
4. **Kurum erişimi:** Üniversite kütüphanesinin veri tabanı abonelikleri (kampüs ağı, VPN veya proxy üzerinden). Ayrıntı: [[database-access]].
5. **Kütüphaneler arası ödünç:** Kurum kütüphanesi üzerinden başka bir kütüphaneden makale veya kitap bölümü istenir.
6. **Yazardan isteme:** Yazara kısa bir e-posta ya da akademik ağ üzerinden istek. Çoğu yazar kendi çalışmasını paylaşır. E-posta gönderilmeden önce kullanıcının onayı alınır.
7. **Kullanıcıya sor:** Hiçbiri sonuç vermezse kaynağın künyesi, denenen kanallar ve önerilen sonraki adımla kullanıcıya bildirilir. Kaynak olmadan yazıma geçilmez (Demir Kural 1).

## Kurallar

- Erişim engeli (CAPTCHA, robots, ödeme duvarı) aşılmaya çalışılmaz; ayna veya arşiv sitesi denenmez.
- İndirilen dosyanın gerçekten aranan eser olduğu ilk sayfadaki başlık ve yazarla doğrulanır; yanlış PDF `sources/` klasörüne konmaz.
- Telifli bir eserin tamamı yapay zekâ sağlayıcısına gönderilmeden önce kurumun ve yayıncının kullanım koşulları göz önünde bulundurulur.

## Gölge kütüphaneler hakkında

Anna's Archive, Sci-Hub ve benzeri siteler varsayılan zincirde yer almaz. Bu sitelerin kullanımı birçok ülkede ve kurumda telif hukukuna ya da kurum politikasına aykırıdır. Kendi sorumluluğunda kullanmak isteyenler için ayrı ve isteğe bağlı bir eklenti vardır: `eklentiler/golge-kutuphane/` (kurulum: `python3 scripts/install_plugin.py eklentiler/golge-kutuphane`). Eklenti kurulu değilse yapay zekâ bu sitelere yönlendirmez.
