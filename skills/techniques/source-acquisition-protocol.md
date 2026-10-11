---
title: "Source Acquisition Protocol"
title_tr: "Kaynak Edinme Protokolü"
node_type: technique
priority: high
description: "A step-by-step logic for acquiring academic sources, moving from automated AI retrieval to guided user intervention, ensuring no crucial citation is left behind."
description_tr: "Akademik kaynakları edinmek için, otonom YZ indirmesinden rehberli kullanıcı müdahalesine kadar uzanan, hiçbir kritik atıfın eksik kalmamasını sağlayan adım adım mantık."
tags: [technique, source-hunting, acquisition, download, manual-search]
links_to:
  - skills/core/iron-rules.md
  - skills/tooling/open-access-chain.md
language: bilingual
version: "1.0"
---

# Source Acquisition Protocol / Kaynak Edinme Protokolü

## Purpose / Amaç

**EN:** To ensure the `/sources/` directory is robust and complete. This protocol bridges the gap between what the AI can find automatically and what the researcher must provide through institutional access or manual effort.
**TR:** `/sources/` dizininin sağlam ve eksiksiz olmasını sağlamak. Bu protokol, YZ'nin otomatik olarak bulabildikleri ile araştırmacının kurumsal erişim veya manuel çaba yoluyla sağlaması gerekenler arasındaki boşluğu doldurur.

---

## 1. The Source Loading Reminder / Kaynak Yükleme Hatırlatması

**Trigger:** Phase 1 (End of Phase) or Phase 2 (Start of Phase).
**AI Action:** Before starting any search, the AI must ask the user to clear their "digital desk":
*"Elinizde bu konuyla ilgili önceden topladığınız tüm kaynakları (PDF'ler, makale taslakları, deney verileri, anket sonuçları vb.) lütfen `/sources/` klasörüne kopyalayın. Temelimizi sizin mevcut literatür taramanız üzerine kuracağız."*

---

## 2. The Acquisition Loop / Edinme Döngüsü

For every required source identified in the Literature Review:

### Level 1: Autonomous AI Retrieval (Otonom İndirme)
**Action:** AI attempts to download the PDF through the legal chain in `open-access-chain` (open access, institutional access, interlibrary loan).
*   *Success:* Save to `/sources/` and notify user.
*   *Failure:* Move to Level 2.

### Level 2: Guided User Download (Rehberli İndirme)
**Action:** AI provides the **direct DOI link** or **stable URL** to the user.
**Prompt:** *"Bu kaynağı otonom olarak indiremedim. Ancak linki burada: [URL]. Lütfen bunu tarayıcınızda açıp (kurumsal VPN/erişim kullanarak) indirin ve `/sources/` klasörüne [Önerilen_Dosya_Adı.pdf] olarak kaydedin."*

### Level 3: Deep Search & Digitization (Derin Arama ve Dijitalleştirme)
**Action:** If no direct link is found, AI provides full metadata and guides the user through manual acquisition.
**Digitization Rule:** If the source is only available in physical print:
- *Instruction:* "Lütfen yayının sayfalarının fotoğrafını çekin veya taratıp PDF olarak kaydedin."
- *File Handling:* User can provide the **absolute path** or **directory location** of the file on their machine.
**AI Action:** TezAtlas will automatically move/copy the file from the provided path to the `/sources/` directory and initiate the OCR pipeline.

---

## 3. Autonomous OCR Quality Monitoring (Background)

**EN:** The AI monitors OCR extraction quality in the background. If it detects a high noise ratio (garbled text, failed character recognition), it will not bother the user with samples but will instead attempt an automated re-scan with different Tesseract parameters or flag the source as "Low-Quality - Review Manually" in the `reading_report.md`.
**TR:** YZ, OCR kalitesini arka planda izler. Eğer yüksek gürültü (bozuk karakterler vb.) tespit ederse, kullanıcıyı meşgul etmez; bunun yerine farklı parametrelerle otomatik tekrar tarama yapar veya kaynağı `reading_report.md` içinde "Düşük Kalite - Manuel İncele" olarak etiketler.

---

## 4. Primary Evidence Loading (Lab/Field Data)

**EN:** If the document type is a Thesis or Technical Report, remind the user that "Sources" aren't just papers.
**TR:** Belge türü Tez veya Teknik Rapor ise, kullanıcıya "Kaynaklar"ın sadece makaleler olmadığını hatırlatın.

**AI Prompt:** *"Deney sonuçlarınız, ham anket verileriniz veya mülakat transkriptleriniz hazır mı? Bunları da `/sources/data/` klasörüne ekleyerek analiz fazına hazır hale getirebiliriz."*
