---
title: "Phase 3 — Reading and Snowball Discovery"
title_tr: "Faz 3 — Okuma ve Kartopu Keşif"
node_type: phase
phase_number: 3
phase_gate_in: "phase-2-sources.md"
phase_gate_out: "phase-4-structure.md"
description: "A cyclic reading loop combining systematic source reading, page-numbered note-taking, and snowball discovery of new sources via footnote-following. This phase is a LOOP until saturation is detected."
description_tr: "Sistematik kaynak okuma, sayfa numaralı not alma ve dipnot takibiyle yeni kaynak keşfini birleştiren döngüsel okuma sürecidir. Bu faz, doygunluk algılanana kadar süren bir DÖNGÜDÜR."
tags: [phase, reading, snowball-sampling, saturation, note-taking, cyclic, loop]
outputs:
  - "notlar/ altında _notlar.md dosyaları (bölüm/kaynak gruplarına göre)"
  - "notlar/INDEX.md (not takip tablosu)"
  - OKUMA_RAPORU.md
  - "Güncellenmiş KAYNAK_ENVANTERI.md"
links_to:
  - skills/techniques/snowball-sampling.md
  - skills/techniques/pdf-reading.md
  - skills/techniques/saturation-check.md
  - skills/techniques/critical-reading.md
  - skills/core/iron-rules.md
  - skills/core/source-policy.md
  - skills/templates/tpl-notes.md
  - skills/templates/tpl-reading-report.md
  - skills/tooling/open-access-chain.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-4-structure.md
language: bilingual
version: "2.4"
---

# Faz 3 — Okuma ve Kartopu Keşif / Phase 3 — Reading and Snowball Discovery

## Bu Fazda Yüklenecek Node'lar

Bu fazı uygulamadan ÖNCE şu dosyaları oku:

- `skills/techniques/pdf-reading.md` — PDF okuma protokolü (metin tabanlı vs taramalı kontrolü, OCR fallback)
- `skills/techniques/snowball-sampling.md` — dipnot takibiyle kaynak keşif algoritması
- `skills/techniques/saturation-check.md` — doygunluk tespiti ve faz çıkış kriteri
- `skills/techniques/critical-reading.md` — eleştirel değerlendirme rubriği (not alma sonrası her kaynak için)

## Amaç

Bu faz bir **DÖNGÜDÜR**, doğrusal değildir. Kaynakları sistematik oku, sayfa numaralı not al, her kaynağın dipnotlarından yeni sources keşfet. Doygunluk algılanana kadar devam et.

Giriş koşulu: [[phase-2-sources]] tamamlanmış ve minimum kaynak sayısı karşılanmış olmalıdır.

## Okuma Döngüsü

```
Kaynak kuyruğundan bir PDF seç
  ↓
ÖN TARAMA (5-10 dk) — tam okumadan önce eleme kararı
  Başlık + özet + sonuç + içindekiler oku
  ├─ RQ1-5 ile bağ yok → ⏭️ ATLANDI (KAPSAM_DIŞI) — OKUMA_RAPORU'nda tek satır gerekçe, dur
  ├─ Güçlü ⭐ AKTİF kaynak zaten bu içeriği kapsıyor → ⏭️ ATLANDI (TEKRAR) — dur
  ├─ Şu an değil ama Faz 6'da lazım olabilir → ⏭️ ATLANDI (ERKEN) — ERKEN havuzuna ekle, dur
  └─ Devam et → tam okuma
  ↓
ARGÜMAN DÜĞÜMÜ — ön atama (taslak, okumadan önce)
  Hangi tez bölümüne/argümanına girebilir? → notlar dosyasında "Taslak bölüm: X.Y" olarak işaretle
  (Gemini önerisi: AI mevcut tez yapısına bakarak öneri üretir, kullanıcı onaylar/değiştirir)
  ↓
[[pdf-reading]] protokolüyle tam okuma (metin tabanlı mı? OCR gerekli mi?)
  ↓
Kaynak oku → sayfa numaralı notlar çıkar → [[tpl-notes]] formatında `notlar/` altına _notlar.md yaz
  ↓
SEVİYE KARARI — okuma sonrası
  ├─ RQ'lardan birini doğrudan yanıtlıyor, özgün katkı var → ⭐ AKTİF
  │   → Argüman düğümünü onayla/revize et
  │   → TEKRAR KONTROLÜ: Aynı argümanı başka ⭐ AKTİF kaynak da söylüyor mu?
  │     Aynı RQ + aynı iddia + aynı kanıt türü → en güçlüsü ⭐ kalır, diğeri ✅ OKUNDU'ya iner
  │     Aynı RQ + farklı kanıt türü → her ikisi ⭐ kalır (tamamlayıcı)
  └─ Tam okundu ama direkt atıf gitmeyecek → ✅ OKUNDU
      → ANAHTAR CÜMLE zorunlu (Gemini önerisi):
        "Bu kaynağı okudum çünkü [X]. Doğrudan atıf gitmiyor çünkü [Y]."
        İki cümle zorunlu; RQ ile bağlantı içermeli; "genel bağlam" gibi belirsiz ifade kabul edilmez
  ↓
`notlar/INDEX.md` kaydını güncelle
  ↓
[[critical-reading]]: Eleştirel değerlendirme yap
  ↓
[[snowball-sampling]] algoritması: dipnotları tara → yeni sources keşfet
  ↓
Okuma raporunu güncelle (Seviye + RQ + Açıklama sütunları)
RQ Kapsam Paneli'ni güncelle
  ↓
Her 5 kaynakta bir [[saturation-check]] çalıştır
  ↓
├─ Doygunluk YOK → döngüye devam
└─ Doygunluk VAR → [[phase-4-structure]]'a geç
```

## Kaynak Kalite Hiyerarşisi

[[source-policy]] düğümü tam kalite hiyerarşisini içerir. Özet:
- Hakemli dergi makalesi > Akademik kitap > Resmi kurumsal rapor > Çalışma kağıdı > Tez > Blog

Bir bölümde yalnızca düşük kalite kaynak varsa uyar: "Bu bölüm için hakemli makale eklenmeli."

## Kaynak Çeşitlilik Metrikleri

`KAYNAK_ENVANTERI.md`'de izle:
```
Dil dağılımı: TR %X / EN %X / Diğer %X
Tarih dağılımı: Klasik (pre-2000) %X / 2000-2020 %X / 2020+ %X
Tür dağılımı: Kitap %X / Makale %X / Rapor %X / Diğer %X
Yazar yoğunluğu: En çok atıf yapılan 3 yazar → Uyarı: tek yazara aşırı bağımlılık
```

## Birincil vs İkincil Kaynak

Mümkün olduğunca birincil kaynak (orijinal eser) tercih et. Birincil bulunamazsa şeffaf ol:
```
"Bodin'in ifadesiyle (Smith, 2020: 45'ten aktaran)..."
```

## Çıktılar

- `notlar/` altında `_notlar.md` dosyaları — şablon: [[tpl-notes]]
- `notlar/INDEX.md` — kaynak bazlı durum panosu
- `OKUMA_RAPORU.md` — doygunluk metrikleri, okunan PDF listesi, kartopu keşifleri — şablon: [[tpl-reading-report]]
- Güncellenmiş `KAYNAK_ENVANTERI.md`
- `notlar/SAVUNMA_ZIRHI.md` — Faz 3 çıkışında üretilir (bkz. Kural 8)

## _notlar.md Tamamlanma Kriteri (Zorunlu)

⭐ AKTİF sources için:
- En az 2 adet sayfa numaralı doğrudan alıntı adayı olmalı
- En az 3 adet sayfa numaralı parafraz argümanı olmalı
- En az 1 adet kartopu keşfi kaydı olmalı (VAR/YOK durumu ile)
- Eleştirel değerlendirme bölümündeki tüm alanlar doldurulmalı
- Yazım planındaki 5 adım doldurulmalı
- Argüman düğümü onaylanmış olmalı (Taslak → Onaylandı)

✅ OKUNDU sources için (kısaltılmış):
- Anahtar Cümle zorunlu: 2 cümle (neden okundu + neden atıf yok)
- En az 1 alıntı adayı
- En az 1 parafraz
- Eleştiri notu (kısa)
- Terfi koşulu belirtilmeli

⏭️ ATLANDI sources için:
- Not dosyası YAZILMAZ
- OKUMA_RAPORU'nda tek satır gerekçe (alt kod: TEKRAR / KAPSAM_DIŞI / ERKEN)

## Danışman Kontrol Noktası

"Okuduğunuz sourcesı ve temel bulgularınızı danışmanınızla paylaştınız mı?"

---

## Methodology Fork / Metodoloji Dallanması

After reading saturation is reached, choose your research methodology. Present each option with its evaluation matrix before the user decides:

---

**A) Theoretical / Conceptual Research**
> ✅ No data collection burden | Faster path to Phase 4 | Strong fit for law, philosophy, humanities
> ⚠️ Contribution claim must be conceptual — empirical validation not possible
> ⭐ Veri yükü: ★☆☆☆☆ | Özgünlük riski: ★★★☆☆ | Süre: ★★☆☆☆ | Metodoloji zorluğu: ★★☆☆☆
> → Proceed directly to Phase 4 (Structure)

**B) Quantitative Research**
> ✅ High generalizability | Statistical power | Clear falsifiability
> ⚠️ Requires hypothesis, valid instruments, and sufficient sample — data collection phase mandatory
> ⭐ Veri yükü: ★★★★☆ | Özgünlük riski: ★★☆☆☆ | Süre: ★★★★☆ | Metodoloji zorluğu: ★★★★☆
> → Faz 3-E1: Research Design → 3-E2: Data Collection → 3-E3: Statistical Analysis → Phase 4

**C) Qualitative Research**
> ✅ Rich, contextual insight | Best for unexplored phenomena | Flexible design
> ⚠️ Saturation harder to prove | Member-checking and ethical approval often required
> ⭐ Veri yükü: ★★★☆☆ | Özgünlük riski: ★★☆☆☆ | Süre: ★★★★☆ | Metodoloji zorluğu: ★★★★☆
> → Faz 3-E1: Interview/Observation Protocol → 3-E2: Data Collection → 3-E3: Coding & Thematic Analysis → Phase 4

**D) Mixed Methods**
> ✅ Triangulation increases validity | Covers both depth and breadth
> ⚠️ Highest time and complexity cost — both quantitative AND qualitative paths must be completed
> ⭐ Veri yükü: ★★★★★ | Özgünlük riski: ★☆☆☆☆ | Süre: ★★★★★ | Metodoloji zorluğu: ★★★★★
> → Complete paths B + C in sequence or parallel; document integration rationale

---

After the user selects, confirm the choice and state what Phase 3 sub-steps are now active.

**Quantitative sub-steps (if B or D chosen):**
- Faz 3-E1: Research Design (hypothesis, variables, measurement instruments)
- Faz 3-E2: Data Collection (survey/experiment execution, sample documentation)
- Faz 3-E3: Statistical Analysis (descriptive stats, inferential tests, effect sizes)
- Output: `data/` folder + `analysis_results.md`

**Qualitative sub-steps (if C or D chosen):**
- Faz 3-E1: Interview / Observation Protocol (guide, ethical approval if needed)
- Faz 3-E2: Data Collection (transcripts, field notes, recordings)
- Faz 3-E3: Coding & Thematic Analysis (codebook, saturation, member-checking)
- Output: `data/` folder + `analysis_results.md`

**GATE: Phase 4 cannot start without analysis_results.md if empirical path chosen.**
