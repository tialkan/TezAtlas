---
title: "Phase 2 — Core Source Hunt"
title_tr: "Faz 2 — Çekirdek Kaynak Avı"
node_type: phase
phase_number: 2
phase_gate_in: "phase-1-topic.md"
phase_gate_out: "phase-3-reading.md"
description: "Find and download the first 15-30 core sources for the thesis topic. Three starting situations: empty /sources/, partially filled, or already stocked. Minimum counts: YL 30, DR 80 before entering Phase 3."
description_tr: "Tez konusu için ilk 15-30 çekirdek kaynağı bul ve indir. Üç başlangıç durumu: boş /sources/, kısmen dolu, zaten dolu. Faz 3'e girmeden önce minimum: YL 30, DR 80."
tags: [phase, source-hunting, download, inventory, minimum-count]
outputs:
  - KAYNAK_ENVANTERI.md
  - "/sources/ klasörü (dolu)"
links_to:
  - skills/core/iron-rules.md
  - skills/core/source-policy.md
  - skills/core/agent-orchestration.md
  - skills/techniques/source-hunting.md
  - skills/techniques/snowball-sampling.md
  - skills/techniques/source-acquisition-protocol.md
  - skills/tooling/open-access-chain.md
  - skills/tooling/database-access.md
  - skills/templates/tpl-source-inventory.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-1-topic.md
  - skills/phases/thesis/phase-3-reading.md
language: bilingual
version: "2.2"
---

# Faz 2 — Çekirdek Kaynak Avı / Phase 2 — Core Source Hunt

## Bu Fazda Yüklenecek Node'lar

Bu fazı uygulamadan ÖNCE şu dosyaları oku:

- `skills/techniques/snowball-sampling.md` — kartopu örnekleme algoritması
- `skills/tooling/open-access-chain.md` — Yasal kaynak edinme zinciri
- `skills/tooling/database-access.md` — kurumsal veritabanları ve açık erişim fallback zinciri
- `skills/core/agent-orchestration.md` — Source Hunter agent tetikleme protokolü

## Amaç

Tez konusu için ilk 15-30 çekirdek kaynağı bulmak ve `/sources/` klasörüne indirmek.

## Başlangıç Durumu Kontrolü

**Durum A — Kaynaklar zaten mevcut** (öğrenci önceden toplamış):
→ Klasör taranır → `KAYNAK_ENVANTERI.md` üretilir → Faz 3'e geçilir

**Durum B — Sıfırdan başlıyor** (sources klasörü boş):
→ Klasör oluşturulur → kaynak avı başlar

**Durum C — Kısmen dolu:**
→ Mevcut sources taranır → eksikler tespit edilir → ek kaynak avı

## Kaynak Bulma Stratejisi

**Adım 1 — Çekirdek liste:**
Anahtar kavramlara ve araştırma sorularına dayanarak AI bir kaynak listesi hazırlar:
- Her araştırma sorusu için en az 3-5 temel kaynak
- Alanın klasik eserleri
- Son 5 yılın önemli çalışmaları
- Disipline özgü temel referanslar

**Adım 2 — Kaynak arama kanalları** (sırayla denenir, detay [[source-acquisition-protocol]]'de):
1. Açık erişim ve yasal kanallar → [[open-access-chain]]
2. Açık erişim veritabanları (SSRN, arXiv, CORE, OpenAlex, Google Scholar)
3. İndirme başarısızsa: Kullanıcıya doğrudan link verilir.
4. Link yoksa: Derin arama protokolü (VPN, ResearchGate, Yazarla iletişim) başlatılır.
5. Kurumsal web siteleri (BIS, IMF, ECB, resmi kurumlar)
6. Üniversite kütüphanesi (kullanıcı aracılığıyla)

**Adım 3 — İndirme, Dosya Adlandırma ve Yeniden Adlandırma Yetkisi:**
```
Bireysel eser:   Yazar_Yıl_Kısa_Başlık.pdf
Kurumsal rapor:  Kurum_Yıl_Kısa_Başlık.pdf
Çok yazarlı:     Yazar1_Yazar2_Yıl_Kısa_Başlık.pdf
```

**AI yetkisi (Faz 2):**
- AI, `KAYNAK_ENVANTERI.md` üretimi sırasında `/sources/` klasöründeki dosya adlarını bu kurala uydurmak için yeniden adlandırabilir.
- Amaç: envanterin tutarlı, aranabilir ve otomatik işlenebilir olması.

**Yeniden adlandırma kuralları:**
1. Boşluklar `_` yapılır.
2. Türkçe karakterler ASCII karşılıklarına çevrilir.
3. Dosya adı `Yazar/Kurum_Yıl_Kısa_Başlık` düzenine getirilir.
4. Uzantı korunur (`.pdf`, `.epub`).
5. Hedef ad çakışıyorsa `_v2`, `_v3` gibi son ek kullanılır.
6. Aşağıdaki dosyalar yeniden adlandırılmaz:
   - `.gitkeep`
   - `README.md`
   - `cookies.txt`

**Kayıt zorunluluğu:**
- Her yeniden adlandırma `KAYNAK_ENVANTERI.md` içinde "Dosya Adı Normalizasyon Kayıtları" bölümüne `eski_ad -> yeni_ad` formatında yazılır.

İndirme zinciri:
```
AI kaynak buldu →
  ├─ Kendisi indirebiliyorsa → indir → /sources/'a kaydet
  └─ İndiremiyorsa → kullanıcıya bildir:
       "Şu kaynak gerekli: [künye]. Link: [url].
        Önerilen dosya adı: Yazar_Yıl_Kısa_Başlık.pdf"
```

## Kaynak Yeterlilik Kontrolü

Faz 3'e geçmeden önce kontrol et:

| Tez Türü | Minimum | Hedef |
|----------|:-------:|:-----:|
| YL tezi | 30 | 50-80 |
| DR tezi | 80 | 150-250 |

Ek kontroller:
- En az 3 farklı kaynak türü (kitap + makale + rapor)
- Tez dili dışında en az 1 dilde kaynak
- Alanın klasik eserleri mevcut mu?

Yeterli değilse → kaynak avına devam.

## Agent Desteği / Agent Support

**Source Hunter Agent** — Faz 2'de araştırma sorusuna dayalı kaynak önerileri üretir.

**Tetikleme koşulu / Trigger condition:**
- `sources/` klasörü boş veya minimum altında
- Kullanıcı "yeni kaynak öner" / "find more sources" derse

**Komut / Command:**
```bash
python3 agents/run.py source_hunter \
  --research-question "[STATUS.md'den araştırma sorusu]" \
  --field "[Alan]" \
  --existing-sources sources/ \
  --language [tr|en|both]
```

**Çıktı:** `KAYNAK_ONERILERI.md` — öneriler kullanıcıya gösterilir, onaylananlar indirilir.

**Agent yoksa:** Manuel kaynak avı [[source-hunting]] ile devam et. Agent opsiyoneldir, engelleyici değil.

---

## Çıktı

`KAYNAK_ENVANTERI.md` — şablon: [[tpl-source-inventory]]
