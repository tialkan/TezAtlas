---
title: "Source Policy — Web vs Local by Phase"
title_tr: "Kaynak Politikası — Faza Göre Web / Yerel"
node_type: foundation
description: "Defines when web access is permitted (discovery in Phases 1-2 only) and when only local /sources/ PDFs may be cited (Phases 6-7). Also covers plagiarism prevention rules."
description_tr: "Web erişiminin ne zaman geçerli olduğunu (sadece Faz 1-2'de keşif) ve sadece yerel /sources/ PDF'lerinin atıflanabileceği zamanları (Faz 6-7) tanımlar. İntihal önleme kurallarını da içerir."
tags: [source-policy, web-access, local-sources, plagiarism, foundation, always-active]
links_to:
  - skills/core/iron-rules.md
  - skills/tooling/open-access-chain.md
  - skills/techniques/source-hunting.md
  - skills/phases/thesis/phase-3-reading.md
used_by:
  - skills/moc/MOC-core.md
  - skills/phases/thesis/phase-1-topic.md
  - skills/phases/thesis/phase-2-sources.md
  - skills/phases/thesis/phase-6-writing.md
language: bilingual
version: "2.1"
---

# Kaynak Politikası / Source Policy

## Temel Kural: Yazımda Sadece Yerel Kaynaklar

Tez yazımında (Faz 6) yalnızca `/sources/` klasöründe fiziksel olarak mevcut olan PDF dosyaları kaynak olarak kullanılabilir.

**YASAKLAR:**
- Web araştırmasından doğrudan atıf yapmak YASAKTIR
- Hafızadan kaynak uydurmak YASAKTIR (bkz. [[iron-rules]] Kural 4)
- Kaynaklar klasöründe olmayan bir esere dipnot düşmek YASAKTIR
- Sayfa numarası tahmin etmek YASAKTIR

**İSTİSNALAR:**
- Faz 1-2'de alan taraması için web kullanılabilir (ama atıf yapılmaz)
- Mevzuat metinleri resmi gazete referansıyla atıflanabilir
- Mahkeme kararları resmi veritabanlarından atıflanabilir

## Faza Göre Web Kullanım Matrisi

| Faz | Web Kullanımı | Atıf Yapılır mı? |
|-----|:---:|:---:|
| Faz 0 (Kimlik) | Hayır | Hayır |
| Faz 1 (Konu keşfi) | **Evet** — alan taraması | **Hayır** |
| Faz 2 (Kaynak avı) | **Evet** — kaynak bulma | **Hayır** — sadece indirme |
| Faz 3 (Okuma) | Kaynak indirme için | **Hayır** |
| Faz 4 (Yapı) | Hayır | Hayır |
| Faz 5 (Protokol) | Hayır | Hayır |
| Faz 6 (Yazım) | **Hayır** | **Evet — sadece /sources/ PDF'lerinden** |
| Faz 7 (Bitiriş) | Hayır | Mevcut dipnotlar |

## İntihal Önleme Kuralları

**Doğrudan alıntı:**
- Kısa alıntı: tırnak içinde ("...")
- Uzun alıntı (3-5+ satır, disipline göre): blok alıntı, girintili
- Her alıntıda sayfa numarası zorunlu
- Doğrudan alıntı oranı paragraf başına max %20

**Parafraz:**
- Kaynak metninden farklı cümle yapısı
- Orijinalin yalnızca fikri alınır
- Parafraz sonrası dipnot zorunlu

**Her paragrafta orijinallik oranı:**
- Min %50: yazarın kendi analizi, yorumu, sentezi
- Max %30: parafraze edilmiş kaynak bilgisi
- Max %20: doğrudan alıntı

## Birincil vs İkincil Kaynak

Mümkün olduğunca birincil kaynak tercih edilir:
- **Birincil:** Orijinal eser (Bodin'in kendi kitabı)
- **İkincil:** O eser hakkında yazılmış analiz

Birincil bulunamıyorsa şeffaf olunur:
```
"Bodin'in ifadesiyle (Smith, 2020: 45'ten aktaran)..."
```

Kaynak bulamıyorsan [[open-access-chain]] ve [[source-hunting]] düğümlerine bak.

## Kaynak Kalite Hiyerarşisi / Source Quality Hierarchy

Genel sıralama (yüksekten düşüğe). Disiplin modülleri bunu override edebilir — bkz. [[MOC-disciplines]]:

| Sıra | Kaynak Türü | Açıklama |
|:----:|------------|---------|
| 1 | Hakemli dergi makalesi | Peer-reviewed, en yüksek akademik güvenilirlik |
| 2 | Akademik kitap (monografi) | Hakemli yayınevi, tek konu derinlemesine |
| 3 | Düzenlenmiş kitap bölümü | Hakemli editör + bölüm yazarı |
| 4 | Resmi kurumsal rapor | BIS, IMF, ECB, resmi devlet kurumları |
| 5 | Çalışma kağıdı (working paper) | Hakemli değil ama kayıtlı (SSRN, arXiv) |
| 6 | Tez / Doktora | Hakemli jüri tarafından savunulmuş |
| 7 | Gazete / Haber | Birincil olay kaynağı, analiz için değil |
| 8 | Blog / Web sitesi | Akademik çalışmada kaynak olarak kullanılmaz |

**Disipline özgü istisnalar:**
- **Hukuk:** Monografiler ve hukuk dergisi makaleleri eşit ağırlıkta; kanun metinleri ve mahkeme kararları ayrı kategori
- **Tıp:** Klinik kılavuzlar ve meta-analizler en üst sırada; vaka raporları düşük hiyerarşide
- **Mühendislik:** Konferans bildirileri (IEEE, ACM) dergi makalesiyle eşdeğer sayılabilir

Bir bölümde yalnızca düşük kalite kaynak varsa (4. sıra ve altı) uyarı ver:
"Bu bölüm için hakemli makale veya akademik kitap eklenmeli."
