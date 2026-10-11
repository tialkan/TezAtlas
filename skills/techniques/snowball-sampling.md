---
title: "Snowball Sampling — Source Discovery Loop"
title_tr: "Kartopu Örnekleme — Kaynak Keşif Döngüsü"
node_type: technique
description: "Algorithm for following footnotes and references inside source PDFs to discover unknown but academically critical works. Applies four selectivity filters to prevent scope creep."
description_tr: "Kaynak PDF'lerindeki dipnot ve referansları takip ederek bilinmeyen ama akademik açıdan kritik eserleri keşfetme algoritması. Kapsam kaymasını önlemek için 4 seçicilik filtresi uygular."
tags: [snowball-sampling, source-discovery, footnotes, bibliography-chaining, iterative, kartopu]
links_to:
  - skills/tooling/open-access-chain.md
  - skills/core/iron-rules.md
  - skills/techniques/source-hunting.md
  - skills/techniques/saturation-check.md
used_by:
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-3-reading.md
  - skills/phases/thesis/phase-6-writing.md
language: bilingual
version: "2.0"
---

# Kartopu Örnekleme / Snowball Sampling

## Algoritma

AI bir PDF okurken kartopu iki farklı tetikleyiciyle başlar:

### Tetikleyici 1: Dipnot / Kaynakça referansı (standart kartopu)

```
Dipnotta kaynak X'e atıf var
  ↓
Seçicilik filtrelerini uygula (aşağıda) → geçti mi?
  ├─ HAYIR → atla, okumaya devam et
  └─ EVET →
       /sources/'da X var mı?
         ├─ EVET → okuma kuyruğuna ekle
         └─ HAYIR → [[open-access-chain]] ile indir
              ├─ Başarılı → /sources/'a kaydet → kuyruğa ekle
              └─ Başarısız → kullanıcıya bildir:
                   "Kaynak X gerekli.
                    Link: [link].
                    Lütfen indirip /sources/'a ekleyin."
```

### Tetikleyici 2: "Aktaran" — İkincil Atıf Tam Zinciri

```
Metinde şu kalıplardan biri görülür:
  "as X argued", "cited in", "aktaran", "quoted in",
  "X'e göre (Y'den)", "X (yıl), yer alan: Y (yıl: s.)"
  ↓
Birincil kaynak (X) tespit edilir
  ↓
ADIM 1 — /sources/ kontrolü
  ├─ VAR → birincil kaynağa git, ilgili sayfayı bul, alıntıyı doğrula
  │         → _notlar.md'ye ATİF: BİRİNCİL olarak kaydet
  │         → ZINCIR TAMAMLANDI
  └─ YOK → ADIM 2'ye geç
  ↓
ADIM 2 — Tam arama zinciri (sırayla, biri bulunca dur)
  1. Açık erişim     (scripts/find_source.py --doi ...)
  2. SSRN / arXiv / CORE / OpenAlex
  3. Kurumsal site   (BIS, IMF, ECB, TCMB, BDDK vb. — resmi PDF)
  4. ResearchGate / Academia.edu
  5. Unpaywall       (DOI ile açık erişim versiyonu)
  ↓
  ├─ BULUNDU →
  │    İndir → Yazar_Yıl_Kısa_Başlık.pdf adıyla /sources/'a kaydet
  │    Toplu OCR kuyruğuna ekle (hailo_ocr_pipeline veya text layer)
  │    OKUMA_RAPORU.md okuma kuyruğuna ekle
  │    KAYNAK_ENVANTERI.md'ye kaydet
  │    _notlar.md'de bu alıntıyı ATİF: BİRİNCİL olarak güncelle
  │    → ZİNCİR TAMAMLANDI
  └─ BULUNAMADI → ADIM 3'e geç
  ↓
ADIM 3 — Kullanıcıya sor
  Kullanıcıya şu mesajı ilet:
  "Birincil kaynak bulunamadı: [Yazar, Yıl, Başlık]
   Lütfen bu kaynağı bulup /sources/ klasörüne ekleyin.
   Önerilen dosya adı: Yazar_Yıl_Kısa_Başlık.pdf"
  Kullanıcı ekleyince → OCR kuyruğuna, okuma kuyruğuna girer,
  _notlar.md'deki alıntı ATİF: BİRİNCİL'e dönüşür.
```

Örnek:
```
Smith (2020: 45): "As Knapp (1905) argued, 'money is a creature of law...'"
→ Birincil: Knapp (1905)
→ /sources/'da YOK
→ Açık erişim (Internet Archive, kamu malı): Knapp_1905_Staatliche_Theorie.pdf bulundu → indirildi
→ /sources/'a eklendi → OCR kuyruğuna girdi → notlar kuyruğuna girdi
→ _notlar.md: ATİF: BİRİNCİL, s.X (Knapp'tan doğrudan)
```

## Seçicilik Filtreleri

Her referans otomatik takip edilmez. Aşağıdaki 4 filtreden **en az biri** karşılanmalıdır:

1. Tez konusuyla doğrudan ilgili mi?
2. Birden fazla kaynakta atıf görüldü mü? *(Sık atıf = kritik eser)*
3. Alanın klasik veya temel eseri mi?
4. Metodolojik olarak kritik mi?

Bu filtrelerin hiçbirini karşılamayan referanslar not edilebilir ama takip edilmez.

## Kaynak Kaydı

Keşfedilen her yeni kaynak `_notlar.md`'ye ve `KAYNAK_ENVANTERI.md`'ye eklenir:
```markdown
### Keşfedilen yeni referanslar (KARTOPU)
- s.45: Knapp (1905) Staatliche Theorie → /sources/'da YOK → İNDİRİLECEK
- s.67: Menger (1892) → /sources/'da VAR → okuma kuyruğuna eklendi
```

## Doygunluk Uyarısı

Kartopu örnekleme yön değiştirebilir: her yeni kaynak kendi dipnotlarını taşır. [[saturation-check]] algoritması ne zaman durulacağını sinyaller — doygunluk yoksa döngü devam eder.
