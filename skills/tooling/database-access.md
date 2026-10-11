---
title: "Academic Database Access — Kurumsal Kütüphane Veritabanları"
title_tr: "Kurumsal Kütüphane Veritabanları Erişim Rehberi"
node_type: tooling
description: "Guide for accessing institutional library databases when open access sources fail. Covers discipline-specific databases (JSTOR, Scopus, LexisNexis, PsycINFO), boolean search strategy, and citation-based discovery. Fallback protocol: Unpaywall/OpenAlex → CORE/arXiv → DergiPark → institutional VPN → interlibrary loan."
description_tr: "Açık erişim kaynakları başarısız olduğunda kurumsal kütüphane veritabanlarına erişim rehberi. Disipline özgü veritabanları (JSTOR, Scopus, LexisNexis, PsycINFO), boolean arama stratejisi ve atıf bazlı keşif. Yedek sıra: Unpaywall/OpenAlex → CORE/arXiv → DergiPark → kurumsal VPN → kütüphaneler arası ödünç."
tags: [tooling, database-access, jstor, scopus, lexisnexis, boolean-search, institutional-library, phase-2, phase-3]
links_to:
  - skills/tooling/open-access-chain.md
  - skills/techniques/source-hunting.md
  - skills/core/source-policy.md
used_by:
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-3-reading.md
  - skills/tooling/open-access-chain.md
language: bilingual
version: "1.0"
---

# Kurumsal Kütüphane Veritabanları / Academic Database Access

## Kaynak Erişim Zinciri (Sırayla Dene)

```
1. /sources/ klasöründe var mı?          → EVET: kullan
   ↓ HAYIR
2. Açık erişim kopyası var mı?             → [[open-access-chain]] protokolü
   ↓ HAYIR
3. Açık erişim sourcesda var mı?         → Aşağıdaki açık erişim kanalları
   ↓ HAYIR
4. ResearchGate / Academia.edu'da var mı?  → Yazarın yüklediği versiyon
   ↓ HAYIR
5. Unpaywall tarayıcı eklentisi ile dene   → Legal açık erişim versiyonu
   ↓ HAYIR
6. Kurumsal VPN ile erişim gerekli         → Kullanıcıya bildir (aşağıdaki format)
```

---

## Disipline Göre Birincil Veritabanları

| Disiplin | Birincil Veritabanı | İkincil |
|----------|--------------------|---------|
| Beşeri bilimler, sosyal bilimler | **JSTOR** | JSTOR Global Plants, Project MUSE |
| STEM, mühendislik, tıp | **Scopus**, **Web of Science** | IEEE Xplore, PubMed |
| Hukuk | **LexisNexis Academic**, **Westlaw** | HeinOnline (hukuk dergileri) |
| Psikoloji, eğitim | **PsycINFO**, **ERIC** | PsycARTICLES |
| İşletme, ekonomi | **Business Source Complete** (EBSCO), **EconLit** | SSRN |
| Türkçe akademik | **DergiPark**, **ULAKBİM TR Dizin** | YÖK Tez Merkezi |

---

## Açık Erişim Fallback Kanalları

Açık erişimde bulunamayan eserler için sırayla dene:

**Preprint ve çalışma kağıtları:**
- **SSRN** (ssrn.com) — ekonomi, hukuk, sosyal bilimler
- **arXiv** (arxiv.org) — STEM, bilgisayar bilimi, matemaTİk, ekonomi
- **CORE** (core.ac.uk) — 200M+ açık erişim makale aggregatörü
- **OpenAlex** (openalex.org) — akademik grafik, erişim linkleri

**Yazarın kendi arşivleri:**
- ResearchGate profil sayfası — yazarlar sık sık tam metni yükler
- Academia.edu — beşeri ve sosyal bilimlerde yaygın
- Yazarın üniversite web sayfası — kişisel yayın listesi

**Otomatik açık erişim tespiti:**
- **Unpaywall** (unpaywall.org/faq) — DOI ver, legal açık erişim versiyonu bul
- **OA Button** (openaccessbutton.org) — bulunamazsa interlibrary loan talebi oluştur

---

## Boolean Arama Stratejisi

Veritabanı aramasında anahtar kelimeler yeterli değildir. Boolean operatörlerini kullan:

**Temel operatörler:**
```
AND → Her iki terimi içeren sonuçlar
      "monetary policy" AND "inflation targeting"

OR  → En az birini içeren sonuçlar (eş anlamlılar için)
      "central bank" OR "monetary authority"

NOT → İstenmeyeni çıkar
      "inflation" NOT "hyperinflation"

"" → Tam ifade (kelime sırası önemli)
      "independent central bank"

*   → Kök türemeleri (wildcards)
      "democra*" → democratic, democracy, democratization
```

**İleri arama teknikleri:**
```
Konu sınırlama: [JSTOR] Subject: Economics AND "monetary policy"
Tarih filtresi: Publication Year: 2015-2024
Kaynak türü: Peer-reviewed only / Scholarly journals only
Dil: English, Turkish, German (gerekirse)
```

---

## Atıf Bazlı Keşif (Citation Tracing)

Bir kaynak bulunduğunda iki yönde genişlet:

**Geriye (Backward citation):** Bu eser hangi çalışmalara atıf yapmış?
→ Dipnotlardan kartopu örnekleme: [[snowball-sampling]]

**İleriye (Forward citation / Cited-by):** Bu esere kim atıf yapmış?
```
Google Scholar: Makalenin altındaki "Atıf yapan X makale" linki
Scopus: "Cited by" sayısına tıkla → atıf yapan listesi
Web of Science: "Times Cited" → atıf ağını gör
```

**Kullanım:** Temel bir klasik eseri bulduysan "cited-by" araması o alana sonradan kimin katkı yaptığını gösterir. 2015'teki bir makaleye 2023'te kim atıf yapmış? Bu kişilerin çalışmaları en güncel literatür.

---

## Scopus/WoS Citation Count Kullanımı

Citation count, kaynak kalitesi için **kaba ama faydalı** bir göstergedir:

| Citation sayısı | Yorum |
|-----------------|-------|
| 500+ | Alan klasiği — neredeyse kesinlikle kullan |
| 100-500 | Önemli çalışma — alanına göre değerlendir |
| 10-100 | Güncel veya niş — içeriğe bak |
| 0-10 | Yeni veya ilgisiz — çok dikkatli değerlendir |

**Uyarı:** Citation count disipline göre çok farklıdır. Tıp ve STEM'de 500+ normal; beşeri bilimlerde 50 çok yüksek sayılabilir. `source-policy.md`'deki disiplin özel notlarına bak.

**Uyarı 2:** Yeni çalışmalar düşük citation'a sahip ama önemli olabilir. Sadece bu metriğe bakma.

---

## Kurumsal VPN Erişimi Gerektiğinde

Üstteki zincirin tamamı başarısız olursa, kullanıcıya şunu söyle:

```
Bu kaynak açık erişimde bulunamadı:
[Tam künye]
[DOI veya URL]

Üniversite kütüphanesi üzerinden erişmek için:
1. Üniversiteni kütüphane VPN'ine bağlan
2. Kütüphane web sitesine git → Veritabanlar → [JSTOR/Scopus/ilgili]
3. DOI veya başlıkla ara
4. PDF'i indir ve /sources/[Yazar_Yıl_Başlık.pdf] olarak kaydet
5. Kaydettiğinde bana söyle, devam ederiz.
```

Kullanıcı VPN erişimini beklerken: `[KAYNAK BEKLENİYOR]` etiketi koy, başka paragrafa geç.

---

## Türkçe Tezler için Ek Kaynak

**YÖK Tez Merkezi** (tez.yok.gov.tr):
- Türkiye'deki tüm YL ve DR tezleri
- Tam metin erişim çoğunda mevcut (ücretsiz)
- Arama: konu + tez türü (YL/DR) + üniversite + yıl

**DergiPark** (dergipark.org.tr):
- Türkçe hakemli dergilerin büyük çoğunluğu
- Açık erişim, ücretsiz

**İSAM** (islamansiklopedisi.org.tr + kutuphane.isam.org.tr):
- İslam araştırmaları ve ilahiyat alanı için vazgeçilmez
