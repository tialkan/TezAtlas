---
title: "Phase 1 — Topic Discovery and Title"
title_tr: "Faz 1 — Konu Keşfi ve Başlık"
node_type: phase
phase_number: 1
phase_gate_in: "phase-0-identity.md"
phase_gate_out: "phase-2-sources.md"
description: "Convert the student's natural-language topic description into an academic thesis title. Extract 10-15 key concepts and formulate 3-5 research questions. Web access permitted for field survey ONLY — no citations yet."
description_tr: "Öğrencinin doğal dille anlattığı konuyu akademik tez başlığına dönüştür. 10-15 anahtar kavram çıkar ve 3-5 araştırma sorusu formüle et. Alan taraması için web kullanımına izin var — henüz atıf yapılmaz."
tags: [phase, topic, title, research-questions, field-survey, web-allowed]
outputs:
  - konu_kesfi.md
links_to:
  - skills/core/source-policy.md
  - skills/templates/tpl-topic-discovery.md
  - skills/core/academic-integrity.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-0-identity.md
  - skills/phases/thesis/phase-2-sources.md
language: bilingual
version: "2.1"
---

# Faz 1 — Konu Keşfi ve Başlık / Phase 1 — Topic Discovery and Title

## Amaç

Öğrencinin doğal dille anlattığı konuyu akademik tez başlığına dönüştürmek, anahtar kavramları belirlemek ve araştırma sorularını formüle etmek.

**ÖNEMLİ:** Bu fazda web kullanılır ama **atıf yapılmaz**. [[source-policy]] Faz 1 sütununa bak: "Web Evet — Atıf Hayır."

## Süreç

**Adım 1 — Doğal Dil Girişi**
Öğrenci konuyu kendi kelimeleriyle anlatır. Örnek:
> "Yapay zekanın iş hukukuna etkisini çalışmak istiyorum, özellikle işçi gözetimi ve algoritmik yönetim ilgimi çekiyor."

**Adım 2 — Alan Taraması (Web)**
AI web araştırması yaparak alanı tarar:
- Bu konuda yapılmış mevcut çalışmalar
- Akademik tartışmanın odak noktaları
- Tespit edilmiş boşluklar (gap)
- Güncel gelişmeler

**Adım 3 — Başlık Önerileri**
AI 5 başlık önerir (tez dilinde + İngilizce):
1. Genel kapsamlı başlık
2. Daraltılmış, spesifik başlık
3. Karşılaştırmalı yaklaşım başlığı
4. Model/öneri odaklı başlık
5. Eleştirel yaklaşım başlığı

Öğrenci seçer, modifiye eder veya yeni öneri ister.

**Adım 4 — Anahtar Kavramlar**
Seçilen başlığa göre 10-15 anahtar kavram çıkarılır (tez dilinde + İngilizce karşılıkları).

**Adım 5 — Araştırma Soruları**
3-5 araştırma sorusu formüle edilir. İyi araştırma sorusu:
- Evet/hayır ile cevaplanmaz
- Spesifiktir ama aşırı dar değil
- Araştırılabilir
- Tez kapsamına sığar (YL: 3-5 soru, DR: 5-7 soru)

**Adım 6 — Çıktıyı Konsolda Göster (Zorunlu)**
`konu_kesfi.md` oluşturulduktan hemen sonra dosyanın tam içeriği kullanıcıya konsolda gösterilir. Kullanıcıdan dosyayı ayrıca açması beklenmez.

**Adım 7 — Kaynak Hazırlığı (Cascade Protokolü)**

Önce sor: "Elinde konuyla ilgili PDF ya da DOI var mı? Varsa `sources/` klasörüne ekle."

Kullanıcı yok derse veya cevap vermezse → **Demir Kural 3 devreye girer (AI önce indirir):**

```
1. Otomatik arama — araştırma sorusuna göre:
   python3 scripts/find_source.py "<araştırma_sorusu>" --output sources/

2. Bulamazsa AI destekli arama (agents.yaml yapılandırıldıysa):
   python3 agents/run.py source_hunter --research-question "<soru>" --field <alan>

3. Kullanıcının bildiği DOI/link varsa:
   python3 scripts/find_source.py --doi "10.xxxx/xxxxx"
   python3 scripts/find_source.py --url "https://arxiv.org/abs/..."

4. Hiçbiri işe yaramazsa → kullanıcıya açıkla:
   "Faz 1→2 geçişi için en az 1 PDF gerekiyor (Demir Kural 1).
    açık erişim kanallarından ([[open-access-chain]]) veya Google Scholar'dan
    konuyla ilgili bir makale indir ve sources/ klasörüne ekle."
```

Kullanıcı hâlâ ekleyemezse: Phase gate'i zorla geçme. Sebebini açıkla, bekle.

## Çıktı

`konu_kesfi.md` oluşturulur — şablon: [[tpl-topic-discovery]]
Dosya yazıldıktan sonra içerik konsolda açıkça gösterilir.

---

## Sonraki Adıma Hazırlık

Faz 2'ye geçmeden önce [[source-acquisition-protocol]] düğümünü okuyun. Elinizdeki tüm kaynakları `/sources/` klasörüne taşımaya hazırlanın.

## Danışman Kontrol Noktası

"Bu başlığı ve araştırma sorularını danışmanınızla paylaştınız mı? Onay aldınız mı?"
