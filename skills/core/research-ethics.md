---
title: "Research Ethics — IRB, KVKK, Data Integrity, and Publication Ethics"
title_tr: "Araştırma Etiği — Etik Kurul, KVKK, Veri Bütünlüğü ve Yayın Etiği"
node_type: foundation
priority: high
description: "Active ethics protocol for all document types. Covers ethics committee approval requirements (Turkish and international), KVKK data protection compliance, informed consent, data retention, conflict of interest disclosure, and publication ethics (self-plagiarism, duplicate submission, authorship). Fires at Phase 0 and pre-submission."
description_tr: "Tüm belge türleri için aktif etik protokolü. Etik kurul onayı gereksinimleri (Türkiye ve uluslararası), KVKK veri koruma uyumu, bilgilendirilmiş onam, veri saklama, çıkar çatışması bildirimi ve yayın etiğini (öz-intihal, mükerrer gönderim, yazarlık) kapsar. Faz 0 ve gönderi öncesinde tetiklenir."
tags: [research-ethics, IRB, ethics-committee, KVKK, informed-consent, data-protection, publication-ethics, conflict-of-interest, always-active]
links_to:
  - skills/core/academic-integrity.md
  - skills/core/iron-rules.md
  - skills/techniques/pre-submission-review.md
used_by:
  - skills/phases/thesis/phase-0-identity.md
  - skills/phases/article/phase-0-claim.md
  - skills/phases/research-proposal/phase-0-context.md
  - skills/phases/grant-proposal/phase-0-funder-analysis.md
language: bilingual
version: "1.0"
---

# Araştırma Etiği / Research Ethics

Etik ihlaller yayını geri çektirir, kariyer bitirir.
Faz 0'da etik yükümlülükler netleştirilir; gönderi öncesinde doğrulanır.

---

## 1. Etik Kurul Onayı Gerekiyor mu? (Phase 0 Tespiti)

Aşağıdaki araştırma türlerinden herhangi biri çalışmada varsa etik kurul onayı **zorunludur:**

| Araştırma Türü | Onay Gerekir mi? | Not |
|---------------|-----------------|-----|
| İnsan katılımcılarla anket / mülakat | **Evet** | Tüm beşeri araştırmalar |
| Gözlem çalışması (katılımcılar farkında) | **Evet** | |
| Klinik / tıbbi veri (kişisel) | **Evet** | KVKK + etik kurul |
| Çocuk ve savunmasız gruplar | **Evet** | Ek korumalar gerekli |
| Hayvan deneyleri | **Evet** | HADYEK onayı (Hayvan Deneyleri Yerel Etik Kurulu) |
| İkincil veri (anonim, herkese açık) | Hayır | Ama kaynak ve telif hakkı kontrol et |
| Belge analizi / literatür taraması | Hayır | |
| Hukuki metin ve mevzuat analizi | Hayır | |
| Kamuya açık istatistik (TÜİK, TCMB vb.) | Hayır | |

**Claude'a tespit için prompt:**
```
Bu çalışmada hangi veri türleri kullanılıyor?
Etik kurul onayı gerektiren bir kategori var mı?
Gerekiyorsa hangi tür onay (üniversite etik kurulu / HADYEK / uluslararası IRB)?
```

---

## 2. Türkiye'de Etik Kurul Süreci

### Üniversite Etik Kurulu

Her üniversitenin kendi etik kurulu vardır (Sosyal ve Beşeri Bilimler Etik Kurulu, Sağlık Bilimleri Etik Kurulu vb.).

**Başvuru için genellikle gereken belgeler:**
- Araştırma Özeti (1-2 sayfa)
- Anket / görüşme soruları
- Bilgilendirilmiş Onam Formu (BOF)
- Veri saklama ve imha planı
- Araştırmacı bilgileri + tez öğrencisiyse danışman imzası

**Onay numarası formatı (TR):**
```
[Üniversite Adı] Sosyal ve Beşeri Bilimler Etik Kurulu
Karar No: [XX/XX]    Tarih: [GG.AA.YYYY]
```

**YÖK ve TR Dizin zorunluluğu:**
- Aralık 2019 sonrası yürütülen beşeri araştırmaları içeren tezler ve makaleler için etik kurul onay numarası **zorunludur.**
- Onay numarası olmayan makaleler TR Dizin'de yayımlanamaz.
- Tezde kapak sayfasının arkasına veya giriş bölümüne eklenir.

### HADYEK (Hayvan Deneyleri)

Hayvan deneyi içeren çalışmalar için üniversitenin HADYEK'ine başvurulur.
Onay belgesi olmadan deney başlatılamaz.

---

## 3. KVKK Uyumu (Kişisel Verilerin Korunması)

**Kanun No. 6698** — Kişisel Verilerin Korunması Kanunu (yürürlük: 7 Nisan 2016)

KVKK, herhangi bir gerçek kişiyle ilgili veri toplandığında uygulanır:
isim, kimlik no, e-posta, konum, sağlık, etnik köken, siyasi görüş vb.

### Araştırmada KVKK Yükümlülükleri

| Yükümlülük | Açıklama |
|-----------|----------|
| **Açık Rıza Beyanı** | Katılımcılar verilerini hangi amaçla nasıl kullanılacağını bilerek onaylamalı |
| **Veri Minimizasyonu** | Araştırma için gerekli olmayan kişisel veri toplanmaz |
| **Amaç Sınırlılığı** | Toplanan veri yalnızca beyan edilen amaç için kullanılır |
| **Saklama Süresi Sınırı** | Araştırma amacı sona erince veri imha edilir veya anonimleştirilir |
| **Güvenli Depolama** | Kişisel veri şifreli ortamda, erişim kontrolüyle saklanır |
| **Yurt Dışı Transfer** | Yurt dışı sunuculara (Google Drive, Dropbox vb.) yalnızca açık rıza ile |

### Bilgilendirilmiş Onam Formu (BOF) — Zorunlu İçerik

```
1. Araştırmacı adı ve kurumu
2. Araştırmanın amacı (sade dille)
3. Katılımın nasıl olacağı (anket, mülakat, gözlem)
4. Süre ve yük (kaç dakika, kaç oturum)
5. Risklerin olmadığı veya neler olduğu
6. Gizlilik ve anonimlik garantisi
7. Katılımın gönüllü olduğu, istediği zaman çekilebileceği
8. Verinin nasıl saklanacağı ve ne zaman imha edileceği
9. Soruları için iletişim bilgisi
10. İmza / dijital onay
```

**Dijital anketlerde:** Google Forms veya benzeri bir araç kullanılıyorsa, ilk sayfada BOF metni ve "Okudum, anladım, katılıyorum" onayı zorunludur.

---

## 4. Uluslararası Standartlar

| Standart | Kapsam | Uygunluk |
|---------|--------|---------|
| **Helsinki Deklerasyonu** | İnsan üzerinde tıbbi araştırma | Tıp + sağlık çalışmaları |
| **Belmont Raporu** | Beşeri araştırma ilkeleri (saygı, iyilik, adalet) | Sosyal bilimler |
| **APA Etik İlkeleri** | Psikoloji + sosyal bilim araştırması | Davranış bilimleri |
| **GDPR** | Avrupa'daki katılımcılardan veri toplanıyorsa | AB vatandaşı katılımcı |

---

## 5. Yayın Etiği

### Öz-İntihal (Self-Plagiarism)

Kendi önceki yayınlarından izinsiz ve kaynak göstermeden alıntı yapmak intihal sayılır.

**Öz-intihal riski oluşturan durumlar:**
```
❌ Yüksek lisans tezinden doktora tezine paragraf kopyalamak
❌ Yayımlanmış makaleden yeni makaleye yöntem bölümünü aynen taşımak
❌ Bir konferans bildirisini dergi makalesine kaynak göstermeden dönüştürmek
```

**Doğru yaklaşım:**
```
✅ Kendi önceki çalışmana atıf yap: (Yazar, 2021)
✅ İkincil kullanım için derginin politikasını kontrol et
✅ Konferans bildirisi → tam makale dönüşümünde editöre bildir
```

### Mükerrer Gönderi (Duplicate Submission)

Aynı makaleyi aynı anda birden fazla dergiye göndermek etik ihlaldir.

```
Kural: Bir dergiden red veya geri çekim olmadan başka dergiye gönderilemez.
İstisna: Preprint sunucularına (arXiv, SSRN) gönderi — çoğu dergi kabul eder.
         Ama bunu gönderim mektubu (cover letter) ile belirt.
```

### Yazarlık Etik Kuralları (ICMJE Standartları)

Yazar sayılmak için **dört kriter** gerekir:
1. Tasarım, veri toplama veya analiz katkısı
2. Taslağın yazılması veya eleştirel revize edilmesi
3. Son sürümün onaylanması
4. Çalışmanın her yönü için hesap verebilirlik kabul

**Hangi durumlar yazarlığı hak etmez:**
```
❌ Yalnızca fon sağlamak (hayır kurucusu yazarlığı / guest authorship)
❌ Yalnızca veri toplamak
❌ Bölüm yöneticisi / danışman olmak (katkı olmadan)
❌ Yalnızca teknik destek vermek
```

**Hayalet yazarlık (Ghost authorship):** Gerçek yazarın listelenmemesi — ciddi etik ihlal.

### Yırtıcı Dergiler (Predatory Journals)

TR Dizin veya JCR/Scopus'ta olmayan, hakemli değil para odaklı açık erişim dergiler.

**Uyarı işaretleri:**
```
- Çok hızlı kabul (<48 saat)
- Editöryel kurul üyeleri doğrulanamıyor
- Impact factor iddiası ama yalnızca bilinmeyen indeksler
- Spam e-postayla davet
- Yayın ücreti ön planda, içerik değil
```

**Kontrol için:** Beall's List (güncel versiyonlar) veya Cabells Scholarly Analytics.

---

## 6. Veri Bütünlüğü ve Saklama

**Araştırma verisi saklama:**
- Ham veri (anket formları, ses kayıtları, transkripler) araştırma sonrası minimum **5 yıl** saklanır
- Tıbbi araştırmalarda bu süre **10-25 yıla** uzayabilir
- Veri imha edildiğinde kayıt tutulur

**Veri uydurma (fabrication) ve manipülasyon (falsification):**
```
❌ Olmayan veriyi uydurmak → akademik kariyeri bitirir
❌ İstenmeyen sonuçları kaldırmak → seçici raporlama / p-hacking
❌ Görselleri manipüle etmek → özellikle bilimsel görüntülerde
```

---

## 7. Zorunlu Beyanlar (Gönderi Öncesi)

Her makale / tez gönderiminde aşağıdakiler kontrol edilmeli:

```
[ ] Etik kurul onayı — numara ve tarih yazıyla verilmiş mi?
    (Gerekiyorsa: beşeri araştırma, hayvan deneyi)

[ ] Bilgilendirilmiş onam — "Tüm katılımcılardan yazılı onam alındı" ifadesi var mı?

[ ] Çıkar çatışması beyanı — "Yazarlar çıkar çatışması olmadığını beyan eder."
    ya da varsa açıkça belirtilmiş mi?

[ ] Fon kaynağı beyanı — destekleyen kurum / proje no belirtilmiş mi?
    Fon yoksa: "Bu araştırma herhangi bir kurum tarafından desteklenmemiştir."

[ ] Veri paylaşım beyanı — veri nerede, nasıl erişilebilir?
    Gizli veriyse: "Veriler gizlilik nedeniyle paylaşılamamaktadır."

[ ] Yazar katkı beyanı (çok yazarlıysa) — CRediT taksonomisi önerilir:
    "YY: Kavramsal çerçeve, yazım. ZZ: Veri analizi, revizyon."
```

---

## 8. Faz Bazlı Etik Eylem Planı

| Faz | Etik Eylem |
|-----|-----------|
| **Faz 0** | Etik kurul gerekip gerekmediğini tespit et → gerekiyorsa başvur |
| **Faz 1–2** | Veri toplama öncesi onay belgesi elde et |
| **Faz 2–3** | Onam formlarını uygula, veriyi güvenli depola |
| **Faz 6** | Beyan metinlerini taslağa ekle |
| **Pre-submission** | Bu bölümdeki kontrol listesini tam çalıştır |

---

## EN — Quick Reference

**Does your study need ethics approval?**
→ Human participants (surveys, interviews, observations) → **Yes**
→ Clinical/medical personal data → **Yes**
→ Animal experiments → **Yes (HADYEK)**
→ Secondary anonymous data, document analysis, literature review → **No**

**Required statements checklist (pre-submission):**
- [ ] Ethics committee approval number + date
- [ ] Informed consent statement
- [ ] Conflict of interest declaration
- [ ] Funding source declaration
- [ ] Data availability statement
- [ ] Author contributions (multi-author)

**Turkey-specific:**
- TR Dizin requires ethics approval number for all human-subjects research published after December 2019
- KVKK (Law No. 6698) applies whenever personal data is collected from participants
- University ethics committees are the standard approval body for social science research
