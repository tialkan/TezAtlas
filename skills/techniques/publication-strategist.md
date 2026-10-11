---
title: "Dynamic Publication Strategist (DPS)"
title_tr: "Dinamik Yayın Stratejisti (DPS)"
node_type: technique
description: "Journal/conference recommendation engine: content to venue matching based on topic, methodology, contribution type. Know submission requirements per target venue. Generate cover letter template."
description_tr: "Dergi/konferans öneri motoru: konu, metodoloji, katkı türüne göre içerik-mekan eşleştirmesi. Hedef mekanın gönderim gereksinimlerini bil. Ön yazı şablonu oluştur."
tags: [technique, publication-strategist, journal-selection, cover-letter, submission, venue-matching]
links_to:
  - skills/tooling/preprints.md
  - skills/core/iron-rules.md
  - skills/core/deadline-mode.md
language: bilingual
version: "1.0"
---

# Dinamik Yayın Stratejisti / Dynamic Publication Strategist

## Ne Yapar? / What It Does

Araştırma tamamlandığında (Faz 7 öncesi veya konferans son teslim öncesi), DPS şu soruları yanıtlar:
1. Bu çalışma *hangi dergiye / konferansa* gitmeli?
2. O mekanın *ne istediğini* biliyor muyuz?
3. *Gönderim paketi* hazır mı?

Aktivasyon: `/yayın-stratejisi` veya Faz 7 geçiş kapısında.

---

## Adım 1 — Çalışma Profili / Work Profile

```
Çalışmanı kısaca anlat:

1. Temel katkı türü:
   A) Ampirik bulgu (yeni veri, deney, anket)
   B) Teorik/kavramsal katkı
   C) Metodolojik yenilik
   D) Sistematik derleme / meta-analiz
   E) Vaka çalışması / uygulama

2. Hedef okuyucu:
   A) Aynı alandaki akademisyenler (disiplin içi)
   B) Disiplinler arası kitle
   C) Politika yapıcılar / uygulayıcılar
   D) Hem akademik hem uygulama

3. Konu alanı: [...]
4. Metodoloji: [nicel / nitel / karma / teorik]
5. Veri kaynağı: [özgün / ikincil / sistematik]
```

---

## Adım 2 — Mekan Önerileri / Venue Recommendations

Girilen profile göre 3-5 dergi veya konferans önerisi:

```
Yayın Profili: [Ampirik, nicel, ekonomi, CBDC]

Önerilen Mekanlar:

1. Journal of International Economics
   Etki göstergesi: [dergi sitesinden / JCR / Scopus'tan bakılacak] | Kapsam: İyi eşleşme
   Beklenen süreç: [derginin kendi istatistiğinden]
   Not: Politika çıkarımı güçlüyse uygun

2. Journal of Monetary Economics
   Etki göstergesi: [bakılacak] | Kapsam: Merkezi
   Beklenen süreç: [derginin kendi istatistiğinden]
   Not: CBDC literatürü yayımlıyorlar (2022-2023)

3. Cambridge Journal of Economics
   Etki göstergesi: [bakılacak] | Kapsam: Heterodoks yaklaşım kabul eder
   Beklenen süreç: [derginin kendi istatistiğinden]

4. SSRN Working Paper (ara adım)
   Önbaskı olarak al, görünürlük kazan → dergi gönderimi

⚠️ Kural: Etki faktörü, çeyreklik (Q), dizin ve süreç süresi hafızadan yazılmaz.
Her değer derginin kendi sitesinden, JCR/Scopus/TR Dizin kaydından okunur ve
erişim tarihiyle yazılır. Okunamayan değer [bakılacak] olarak kalır.
```

---

## Adım 3 — Gönderim Gereksinimleri / Submission Requirements

Hedef mekan belirlendikten sonra kontrol listesi:

```
[DERGI ADI] Gönderim Kontrol Listesi:

Format:
□ Sayfa sınırı: [X]
□ Kelime sınırı: [X]
□ Atıf stili: [APA / Chicago / Vancouver / dergi spesifik]
□ Anonim gönderim: [Evet / Hayır]
□ Başlık sayfası ayrı mı?

Zorunlu belgeler:
□ Ana metin (anonim)
□ Başlık sayfası (yazar bilgileri)
□ Öz / Abstract ([X] kelime)
□ Anahtar kelimeler ([X] adet)
□ Açıklama beyanı (çıkar çatışması, etik onay)
□ Ön yazı (cover letter)
□ Veri erişim beyanı

⚠️ Dergi web sitesinden güncel bilgileri doğrula — bu kontrol listesi şablon niteliğindedir.
```

---

## Adım 4 — Ön Yazı Şablonu / Cover Letter Template

```markdown
[TARİH]

Sayın Editör,

"[MAKALE BAŞLIĞI]" başlıklı makalemizi [DERGI ADI] dergisine
değerlendirilmek üzere sunuyoruz.

Bu çalışmada [ANA KATKIYI BİR CÜMLEYLE AÇIKLA].

Çalışmanın [DERGI]'ye özgün katkısı şudur: [NİÇİN BU DERGİ].

Eş zamanlı gönderim bulunmamakta; çalışma başka bir dergide
değerlendirme sürecinde değildir.

Saygılarımla,
[AD SOYAD]
[UNVAN, KURUM]
[E-POSTA]
```

---

## Konferans Özel Stratejisi

Konferans bildirisi için:
- **Erken gönderim**: çoğu konferansta abstract kabul → full paper döngüsü var
- **Tam metin önce mi, abstract mı?**: Alan normunu kontrol et (CS → tam metin; Sosyal Bil. → abstract yeterli)
- **Proceedings vs. journal track**: IEEE, ACM vb. konferanslar proceedings yayınlar — dergi puanlamasından farklı

---

## Türkiye Özel: Dergi Puanlama

```
TR Dizin: Türkçe akademik dergiler için ulusal endeks
ULAKBİM Sosyal Bilimler: Sosyal bilim dergileri
YÖK ESBD: Uluslararası dergi puanlama (Q1-Q4)

TÜBİTAK 1001/1003 projeleri: Q1-Q2 zorunluluğu var (proje tipine göre değişir)
Doçentlik: Yazar sırası + dergi puanı kritik — alan kriterlerini kontrol et
```
