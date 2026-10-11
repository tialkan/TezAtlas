---
title: "Phase 0 — Identity Collection"
title_tr: "Faz 0 — Kimlik Toplama"
node_type: phase
phase_number: 0
phase_gate_in: null
phase_gate_out: "phase-1-topic.md"
description: "Collect the 8 required identity fields (student, university, institute, degree, advisor, language, discipline, topic). Auto-detect citation system and thesis structure tradition. Load university template and discipline module."
description_tr: "8 zorunlu kimlik alanını topla (öğrenci, üniversite, enstitü, derece, danışman, dil, disiplin, konu). Atıf sistemi ve tez yapı geleneğini otomatik tespit et. Üniversite şablonunu ve disiplin modülünü yükle."
tags: [phase, identity, onboarding, discipline-loading, university-format]
outputs:
  - proje_kimlik.md
links_to:
  - skills/core/iron-rules.md
  - skills/moc/MOC-disciplines.md
  - skills/moc/MOC-universities.md
  - skills/moc/MOC-citations.md
  - skills/templates/tpl-project-identity.md
  - skills/core/academic-integrity.md
  - skills/techniques/contribution-claim.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-1-topic.md
language: bilingual
version: "2.2"
---

# Faz 0 — Kimlik Toplama / Phase 0 — Identity Collection

## Amaç

Projenin temel kimlik bilgilerini toplamak. Bu bilgiler tüm sonraki fazlarda kullanılır.

## Sorulacak Bilgiler — UYGULAMA KURALLARI

> **KRİTİK:** Aşağıdaki sorular SERBEST METİN olarak sorulacak.
> Serbest metin soruları için AskUserQuestion tool'u KULLANMA —
> sadece düz metin olarak sor ve kullanıcının cevabını bekle.
> AskUserQuestion tool'unu YALNIZCA gerçek seçenekler sunan sorular için kullan
> (Program Türü, Dil, Disiplin gibi).

**Serbest metin olarak sor (tek tek, sırayla):**

1. "Adınız soyadınız nedir?" → cevabı bekle
2. "Hangi üniversitede okuyorsunuz?" → cevabı bekle
3. "Hangi enstitüde öğrenim görüyorsunuz? (ör. Sosyal Bilimler Enstitüsü)" → cevabı bekle
4. "Anabilim dalınız nedir?" → cevabı bekle
5. Program türü → **AskUserQuestion** ile sor: Yüksek Lisans / Doktora
6. "Danışmanınızın adı soyadı ve unvanı nedir?" → cevabı bekle
7. Tez dili → **AskUserQuestion** ile sor: Türkçe / İngilizce / Almanca / Diğer
8. Disiplin → **AskUserQuestion** ile sor: Hukuk / Mühendislik / Sosyal Bilimler / Fen / Tıp / İşletme / Eğitim / Diğer

**İsteğe bağlı (serbest metin):**
9. "Tez teslim tarihiniz var mı? Varsa belirtin, yoksa 'yok' yazın."
10. "Üniversitenizin tez yazım kılavuzu PDF'i veya linki var mı?"
11. Atıf sistemi → **AskUserQuestion** ile sor (sadece kullanıcı manuel tercih isterse)

**YASAK:** Hiçbir soruyu placeholder metin içeren seçenek listesi olarak gösterme.
Örneğin "Ad ve soyadımı gir", "Üniversite adını gir" gibi ifadeler seçenek OLAMAZ —
bunlar action hint'tir, asla gerçek cevap değildir. Kullanıcı boş cevap verirse
(sadece enter'a basarsa) soruyu tekrar sor.

## Zorunlu Otomasyon Adımı

Faz 0 sırasında AI, `/sources/` klasörünü **boş olsa bile** oluşturur:

```bash
mkdir -p sources
```

Ardından kullanıcıya şu yönlendirme yapılır:
"Literatür taramasında keşfettiğiniz yayınların PDF'lerini `/sources/` klasörüne ekleyin."

## Otomatik Tespitler

**Atıf sistemi** (üniversite + disipline göre varsayılan) — tam tablo [[MOC-disciplines]]'da:
- Hukuk → Chicago Notes-Bibliography veya OSCOLA
- Sosyal bilimler → APA 7
- Mühendislik/Fen → IEEE
- Tıp → Vancouver
- İşletme → APA veya Harvard

**Tez yapı geleneği:**
- Hukuk → Giriş + 2-3 Bölüm + Sonuç
- STEM → IMRAD veya Introduction + Literature + Method + Results + Discussion
- Sosyal bilimler → her ikisi de olabilir

**Dil kuralları:**
- Türkçe → UTF-8 zorunlu, ş/ç/ğ/ı/ö/ü kontrol
- İngilizce → American/British English tutarlılığı

## Yükleme Adımları

1. `/sources/` klasörünü oluştur (yoksa) ve kullanıcıyı kaynak eklemeye teşvik et
2. [[MOC-universities]] üzerinden üniversite şablonunu yükle
   - **Listede varsa:** doğrudan yükle (ODTÜ, İTÜ, Boğaziçi, Hacettepe, Ankara, ASBÜ)
   - **Listede yoksa → Otomatik Türetme:**
     a. `templates/universities/ornek.yaml` dosyasını aç
     b. Kullanıcıya sor: "Üniversitenizin tez yazım kılavuzu var mı? PDF veya link paylaşabilirsiniz."
     c. Kılavuz paylaşıldıysa → ilgili alanları (kenar boşlukları, yazı tipi, satır aralığı) kılavuzdan oku → ornek.yaml'ı doldur
     d. Kılavuz yoksa → standart değerleri kullan ve kullanıcıyı bildir: "Üniversite kılavuzunuz eklendiğinde güncelleyebiliriz."
3. [[MOC-disciplines]] üzerinden disiplin modülünü yükle (tek bir modül)
4. Disipline göre varsayılan atıf sistemini tespit et; [[MOC-citations]] üzerinden rehberi yükle

## Çıktı

`proje_kimlik.md` oluşturulur — şablon: [[tpl-project-identity]]

---

## Katkı İddiası Kalkanı

Faz 0'ı kapatmadan önce özgünlük protokolünü çalıştır:
→ [[techniques/contribution-claim]]
