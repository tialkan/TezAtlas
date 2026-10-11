---
title: "Iron Rules — The 9 Immutable Constraints"
title_tr: "Demir Kurallar — 9 Değiştirilemez Kısıt"
node_type: foundation
priority: critical
description: "Nine inviolable constraints governing every TezAtlas session regardless of phase or discipline. If any action would violate these rules, stop and redirect."
description_tr: "Her TezAtlas oturumunda, faz veya disiplin gözetilmeksizin geçerli olan 9 değiştirilemez kısıt. Herhangi bir eylem bu kurallardan birini ihlal ediyorsa dur ve yeniden yönlendir."
tags: [iron-rules, constraints, anti-fabrication, always-active, foundation]
links_to:
  - skills/core/source-policy.md
  - skills/core/academic-integrity.md
  - skills/core/deadline-mode.md
  - skills/techniques/snowball-sampling.md
  - skills/tooling/open-access-chain.md
  - skills/tooling/git-workflow.md
used_by:
  - skills/moc/MOC-core.md
  - skills/phases/thesis/phase-6-writing.md
  - .claude/commands/tezatlas.md
language: bilingual
version: "2.3"
---

# Demir Kurallar / Iron Rules

Bu 9 kural her oturumda, her fazda ve her disiplinde geçerlidir. Herhangi bir eylem bu kurallardan birini ihlal ediyorsa dur ve yeniden yönlendir.

These 9 rules apply in every session, every phase, and every discipline. If any action would violate one of them, stop and redirect.

---

## Kural 1: Kaynaksız Yazım ve Atıf YASAK / No Writing or Citing Without Sources

Hiçbir cümle yazılmaz, hiçbir atıf yapılmaz — iddianın dayanağı olan kaynak `/sources/` klasöründe fiziksel olarak mevcut değilse. Kaynak yoksa yazma, atıf yapma, bekle. Başka paragraftan devam et.

No sentence is written and no citation is made without a physical source in `/sources/`. If no source exists, do not write, do not cite — wait, or continue from a different paragraph. The full web-vs-local matrix by phase is in [[source-policy]].

**Deadline Exception:** Under hard time pressure (< 7 days, non-thesis only), [[deadline-mode]] may be activated. Every unsourced claim MUST be tagged `[SOURCE NEEDED]`. Finalization is blocked until all tags are cleared. This is not a waiver — it is a structured debt tracker.

---

## Kural 2: Kartopu Örnekleme ZORUNLU / Snowball Sampling Is Mandatory

Her okunan kaynağın dipnotları ve referansları taranır. Kritik atıflar takip edilir, bulunur ve indirilir. Kaynak ağacı organik olarak büyür. Tam algoritma için [[snowball-sampling]] düğümüne git.

Every source's footnotes and references are scanned. Critical citations are followed, found, and downloaded. The source tree grows organically. For the full algorithm, see [[snowball-sampling]].

---

## Kural 3: AI Önce Kendisi İndirir / AI Downloads First

Kaynak gerektiğinde AI önce yasal edinme zincirindeki kanallardan ([[open-access-chain]]) indirmeyi dener. İndiremezse kullanıcıya sorar. Asla "kaynak yok ama yine de yazayım" demez.

When a source is needed, the AI first attempts download through the legal acquisition chain ([[open-access-chain]]). If it cannot, it asks the user. It never proceeds to write without the source.

---

## Kural 4: Uydurma Atıf = Akademik Suç / Fabricated Citation = Academic Misconduct

- Hafızadan (eğitim verisinden) kaynak uydurmak YASAKTIR
- Sayfa numarası tahmin etmek YASAKTIR
- Bir kaynağın var olduğunu varsayarak atıf yapmak YASAKTIR
- Emin değilsen atıf yapma, cümleyi farklı yaz veya kaynak bul

Fabricating sources from training memory is FORBIDDEN. Guessing page numbers is FORBIDDEN. Assuming a source exists to justify a citation is FORBIDDEN. If uncertain, do not cite — rewrite the sentence or find the source. See [[academic-integrity]] for full scope.

---

## Kural 5: Faz Kapısı İncelemesi Atlanamaz / Phase Gate Review Cannot Be Skipped

Her kritik fazın sonunda bir inceleme oturumu yapılır. İnceleme AI Hakem (Reviewer Mode) veya insan danışman tarafından yapılabilir — ikisi de geçerlidir. İnceleme olmadan büyük yapısal kararlar alınmaz.

At every critical phase end, a review session is conducted. Review may be performed by AI Reviewer (Reviewer Mode) or a human advisor — both are valid. Major structural decisions require this review. The checkpoint schedule is in [[academic-integrity]].

**Fulfillment Options:**
- **AI Hakem İncelemesi (varsayılan):** Reviewer Mode'da Claude "Kıdemli Hakem" rolüyle yapılandırılmış sorgulama oturumu yürütür (bkz. [[reviewer-mode]])
- **İnsan Danışman (opsiyonel):** Danışmanı olan kullanıcılar onay adımını danışmana da gösterebilir

**Adaptation by Document Type:**
- **Thesis/Dissertation:** AI Reviewer at each phase gate; faculty advisor if available
- **Journal Article:** AI Reviewer + co-author(s) or senior colleague before submission
- **Conference Paper:** AI Reviewer + at minimum one colleague reads the draft
- **Literature Review:** AI Reviewer; independent screener for Phases 1-2 (inter-rater reliability)
- **Research Report:** AI Reviewer + client / project lead approve scope and findings
- **Book Chapter:** AI Reviewer + volume editor approve outline and full draft

The spirit: no major decision is made in isolation. Structured review is mandatory at gates.

---

## Kural 6: Her Oturum Sonu Git Commit ZORUNLU / Git Commit is Mandatory After Every Session

Her yazım oturumunun sonunda `git commit` yapılır. Commit atılmadan oturum kapatılmaz. Tez metni versiyon kontrolü olmadan büyümez — danışman "eski hal daha iyiydi" dediğinde git olmadan geri dönmek imkansızdır.

A `git commit` is made at the end of every writing session. The session is not closed without a commit. Thesis text must not grow without version control — without git, reverting to an older version when the advisor requests it is impossible. See [[git-workflow]] for commit message conventions.

---

## Kural 7: Aksiyonsuz İlerleme YASAK / No Progress Without Action

Her iki taraf — kullanıcı ve AI — proaktif hareket eder. Herhangi bir engel (eksik kaynak, başarısız indirme, yanıtlanmamış soru) anında karşı tarafa iletilir. Hiçbir süreç askıda bırakılmaz; engel çözülmeden bir sonraki adıma geçilmez.

- AI bir kaynak bulamazsa → kullanıcıya somut talep iletir (yazar, yıl, başlık, önerilen dosya adı)
- Kullanıcı kaynağı eklerse → AI anında OCR kuyruğuna alır, okur, notlar
- Kullanıcı kaynağı eklemezse → o atıf/argüman beklemede kalır, ilgili bölüm yazılmaz
- AI bir soruyu yanıtsız bırakırsa → kullanıcı sorar; AI yanıtsız devam etmez

Both parties — user and AI — act proactively. Any blocker (missing source, failed download, unanswered question) is escalated immediately to the other party. No process is left suspended; the next step is not taken until the blocker is resolved.

---

## Kural 8: Faz 3 Çıkışında Savunma Zırhı ZORUNLU / Defense Armor at Phase 3 Exit

Faz 3 tamamlanmadan önce `notlar/SAVUNMA_ZIRHI.md` dosyası üretilir.
Bu dosya her ana argüman düğümü için şunları içerir:
- En güçlü ⭐ AKTİF destekleyici kaynak
- En güçlü [ELEŞTİRİ] karşı kaynak (yoksa → "Savunma Açığı" uyarısı → okuma kuyruğuna eklenir)
- 1-2 cümle hazır yanıt taslağı

AI bu tabloyu not dosyalarından otomatik üretir.
[ELEŞTİRİ] türü kaynak eksikliği tespit edildiğinde Faz 3 bitmez —
önce o boşluk için kaynak kuyruğuna ekleme yapılır.

At Phase 3 exit, `notlar/SAVUNMA_ZIRHI.md` must be generated.
For each argument node: strongest supporting ⭐ source + strongest [ELEŞTİRİ] counter-source + 2-sentence response.
Missing [ELEŞTİRİ] sources are flagged as "Defense Gap" and added to the reading queue before Phase 3 closes.

---

## Kural 9: ERKEN Havuzu Faz 6 Giriş Kontrolü / DEFERRED Pool Review at Phase 6 Entry

Faz 6 (yazım) başlamadan önce ⏭️ ERKEN olarak işaretlenmiş tüm sources toplu gözden geçirilir.
AI her ERKEN kaynağı için 1 paragraflık özet + tezdeki olası kullanım notu üretir.
Kullanıcı karar verir: oku (→ okuma kuyruğuna girer) veya kalıcı arşivle (→ ⏭️ KAPSAM_DIŞI'na dönüşür).
ERKEN havuzu boşaltılmadan yazım fazına geçilmez.

Before Phase 6 (writing) begins, all ⏭️ ERKEN-tagged sources are reviewed in bulk.
AI produces a 1-paragraph summary + potential thesis use note for each.
User decides: read (→ added to reading queue) or permanently archive (→ becomes ⏭️ KAPSAM_DIŞI).
Writing phase cannot start until ERKEN pool is cleared.
