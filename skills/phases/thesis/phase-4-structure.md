---
title: "Phase 4 — Structure Design"
title_tr: "Faz 4 — Yapı Tasarımı"
node_type: phase
phase_number: 4
phase_gate_in: "phase-3-reading.md"
phase_gate_out: "phase-5-protocol.md"
description: "Design the thesis structure AFTER reading, not before. Synthesize reading notes into themes, propose table of contents, map sources to sections, set word targets. CRITICAL: Structure requires advisor approval before writing begins."
description_tr: "Tez yapısını OKUMADAN SONRA tasarla, öncesinde değil. Okuma notlarını temalara sentezle, içindekiler taslağı öner, sourcesı bölümlerle eşleştir, kelime hedeflerini belirle. KRİTİK: Yapı danışman onayı olmadan yazıma geçilemez."
tags: [phase, structure, table-of-contents, source-mapping, advisor-approval, critical]
outputs:
  - yapi_taslagi.md
  - SOURCE_MAP.md
links_to:
  - skills/moc/MOC-disciplines.md
  - skills/techniques/argument-mapping.md
  - skills/techniques/argument-evaluation.md
  - skills/templates/tpl-outline.md
  - skills/templates/tpl-source-map.md
  - skills/core/academic-integrity.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-3-reading.md
  - skills/phases/thesis/phase-5-protocol.md
language: bilingual
version: "2.1"
---

# Faz 4 — Yapı Tasarımı / Phase 4 — Structure Design

## Bu Fazda Yüklenecek Node'lar

Bu fazı uygulamadan ÖNCE şu dosyaları oku:

- `skills/techniques/argument-mapping.md` — okuma notlarından yapı çıkarma tekniği (5 adım: küme → RQ eşleme → boşluk tespiti → bölüm sınırları → yapi_taslagi)
- `skills/techniques/argument-evaluation.md` — yapı taslağındaki argümanların mantıksal kalitesini test et (zincir bütünlüğü, çelişki tespiti, karşı argüman kontrolü)

## Amaç

Faz 3'teki okumalardan çıkan yapıyı tasarlamak. **Yapı okumalardan ÇIKAR**, okumadan önce uydurulmaz.

## Süreç

**Adım 1 — Okuma Sentezi**
`_notlar.md` dosyaları gözden geçirilir. Ana temalar, argüman hatları ve boşluklar belirlenir.

**Adım 2 — Yapı Önerisi**
[[MOC-disciplines]] üzerinden yüklenen disiplin modülüne göre yapı seçeneklerini aşağıdaki değerlendirme matrisiyle sun:

---

**A) Hukuk Yapısı** — Giriş → Bölüm 1 (Teori + Mevcut Durum) → Bölüm 2 (Analiz/Öneri) → Sonuç
> ✅ Hukuk dergilerinin ve jürilerin beklentisiyle tam uyumlu | Normatif-analitik akışa ideal
> ⚠️ Ampirik bölüm eklenmesi gerekirse yapı zorlanır; esnek değil
> ⭐ Disiplin uyumu: ★★★★★ | Esneklik: ★★☆☆☆ | Danışman onay kolaylığı: ★★★★★

**B) STEM / IMRaD Yapısı** — Introduction → Literature → Methodology → Results → Discussion → Conclusion
> ✅ Uluslararası standart; hakemler tarafından anında tanınır | Açık katkı bölümü (Results)
> ⚠️ Sosyal bilimler veya hukuk tezine uygulanırsa yabancı durabilir
> ⭐ Disiplin uyumu: ★★★★★ (STEM) / ★★☆☆☆ (diğer) | Esneklik: ★★★☆☆ | Uluslararası görünürlük: ★★★★★

**C) Sosyal Bilimler Yapısı** — Giriş → Kavramsal Çerçeve → Yöntem → Bulgular → Tartışma → Sonuç
> ✅ Hem teorik hem ampirik bölümlere yer açar | Jüri beklentisiyle örtüşür
> ⚠️ Kavramsal çerçeve bölümü zayıf tutulursa okuma fazının emeği görünmez
> ⭐ Disiplin uyumu: ★★★★★ (sos. bil.) | Esneklik: ★★★★☆ | Teorik derinlik göstergesi: ★★★★☆

**D) Tıp / Klinik Yapısı** — Introduction → Methods → Results → Discussion (kısa IMRaD)
> ✅ En kompakt format | Klinik araştırmalar ve sağlık bilimleri için endüstri standardı
> ⚠️ Literatür derinliğini gösterme alanı kısıtlı; uzun teorik tezlere uymuyor
> ⭐ Disiplin uyumu: ★★★★★ (tıp) / ★☆☆☆☆ (diğer) | Kompaktlık: ★★★★★ | Esneklik: ★★☆☆☆

---

Kullanıcı seçim yaptıktan sonra seçilen yapıyı temel alarak alt bölüm önerisi üret.

**Adım 3 — Alt Bölümler ve İçindekiler**
Her bölümün alt bölümleri belirlenir. Detaylı içindekiler taslağı oluşturulur.

**Adım 4 — Kaynak Eşleştirme**
Her alt bölüm için çekirdek sources eşlenir (şablon: [[tpl-source-map]]):
```
Bölüm 1.1: → kaynak_a.pdf, kaynak_b.pdf, kaynak_c.pdf (3+)
Bölüm 1.2: → kaynak_d.pdf, kaynak_e.pdf (min 3 kaynak uyarısı)
```
Bir bölümde 3'ten az kaynak varsa → uyarı: "Bu bölüm için ek kaynak gerekli."

**Adım 5 — Uzunluk Hedefleri**

| Tez Türü | Hedef |
|----------|-------|
| Hukuk YL | 40.000-80.000 kelime |
| Sosyal bilimler YL | 25.000-50.000 kelime |
| STEM YL | 15.000-30.000 kelime |
| DR tezi | YL'nin 1.5-2 katı |

**Adım 6 — Yazım Sırası**
Genellikle: Kavramsal/teorik çerçeve → Yöntem/analiz → Giriş (önceki bölümler netleşince) → Sonuç (en son)

## Çıktılar

- `yapi_taslagi.md` — şablon: [[tpl-outline]]
- `SOURCE_MAP.md` — şablon: [[tpl-source-map]]

## Danışman Kontrol Noktası (**KRİTİK**)

"İçindekiler taslağını danışmanınıza gösterin ve onay alın. **Yapı onaylanmadan [[phase-5-protocol]]'e geçilmez ve yazıma başlanmaz.**"
