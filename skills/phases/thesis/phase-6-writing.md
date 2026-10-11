---
title: "Phase 6 — Read and Write"
title_tr: "Faz 6 — Oku ve Yaz"
node_type: phase
phase_number: 6
phase_gate_in: "phase-5-protocol.md"
phase_gate_out: "phase-7-finalization.md"
description: "Write thesis sections by reading sources, taking notes, and composing paragraph by paragraph. Three session types: reading-only, writing-only, or combined. Writing is BLOCKED if no source exists for a claim."
description_tr: "Kaynakları okuyarak, not alarak ve paragraf paragraf yazarak tez bölümlerini üret. Üç oturum türü: sadece okuma, sadece yazım veya kombine. İddia için kaynak yoksa yazım DURUR."
tags: [phase, writing, reading, session-structure, note-taking, source-blocked, loop]
outputs:
  - "Tez bölüm dosyaları (chapter_X_Y.md)"
  - "Güncellenmiş MEMORY.md ve DURUM_OZETI.md"
links_to:
  - skills/core/iron-rules.md
  - skills/core/source-policy.md
  - skills/core/quality-control.md
  - skills/core/agent-orchestration.md
  - skills/techniques/snowball-sampling.md
  - skills/techniques/session-structure.md
  - skills/techniques/critical-reading.md
  - skills/techniques/argument-evaluation.md
  - skills/techniques/drafting-alternatives.md
  - skills/techniques/paragraph-coherence.md
  - skills/techniques/natural-voice.md
  - skills/templates/tpl-notes.md
  - skills/tooling/open-access-chain.md
  - skills/tooling/database-access.md
used_by:
  - skills/moc/MOC-phases.md
  - skills/phases/thesis/phase-5-protocol.md
  - skills/phases/thesis/phase-7-finalization.md
language: bilingual
version: "2.2"
---

# Faz 6 — Oku ve Yaz / Phase 6 — Read and Write

## Bu Fazda Yüklenecek Node'lar

Bu fazı uygulamadan ÖNCE şu dosyaları oku:

- `skills/core/guided-writing-mode.md` — **BİRİNCİL YAZIM PROTOKOLÜ**: A/B seçenekleri, Akademik Yazım Notu, kaynak kanıtı formatı
- `skills/techniques/session-structure.md` — oturum başı/sonu ritüeli, tam protokol
- `skills/tooling/git-workflow.md` — oturum sonu zorunlu commit prosedürü
- `skills/techniques/critical-reading.md` — Faz 6'da yeni kaynak okunduğunda eleştirel değerlendirme
- `skills/techniques/argument-evaluation.md` — bölüm yazıldıktan sonra argüman mantık kontrolü
- `skills/techniques/drafting-alternatives.md` — A/B/C/D seçenek matrisi, puanlama tablosu
- `skills/core/smart-choice-presentation.md` — makro kararlarda (metodoloji, yapı, strateji, bölüm sırası) avantaj/dezavantaj + yıldız matrisi
- `skills/techniques/paragraph-coherence.md` — paragraftan paragrafa bağlam sürekliliği, tekrar önleme, argüman izleme
- `skills/techniques/natural-voice.md` — YZ kelime kara listesi, burstiness kontrolü, yazım stili profili eşleştirme
- `skills/tooling/database-access.md` — yazım sırasında bulunamayan kaynak için fallback zinciri
- `skills/core/agent-orchestration.md` — Citation Verifier ve Methodology Checker tetikleme protokolü

## Amaç

Kaynaklardan okuyarak, not alarak ve Guided Writing Mode protokolüyle tez metnini bölüm bölüm üretmek. AI her paragraf için A/B seçenekleri + Akademik Yazım Notu sunar; kullanıcı seçer, yönlendirir ve sahiplenir.

## Oturum Yapısı

Tam oturum ritüeli [[session-structure]]'da. Özet:

**OTURUM BAŞI:** tezprotokol.md + MEMORY.md + DERSLER.md + TERMINOLOJI.md + ilgili `_notlar.md` oku → hedef bölümü belirle

**AŞAMA 1 — OKUMA:** En az 3 PDF oku → sayfa numaralı not → [[snowball-sampling]] döngüsü → `_notlar.md` güncelle → yazım planı yap

**AŞAMA 2 — YAZIM:** `_notlar.md`'ye bakarak paragraf paragraf yaz → **Bölüm başında Argüman İzleyici oluştur** (`paragraph-coherence.md`) → **Her paragraf için `drafting-alternatives.md` kuralına göre A/B/C/D seçenekleri ve puanlama tablosu sun** (önceki paragrafın PBK'sı zorunlu girdi) → Kullanıcı seçim yapsın → **PBK güncelle + Argüman İzleyici'yi işaretle** → her paragrafta doğrulanmış dipnot → terminoloji kontrolü → [[quality-control]] kontrol listesi

**OTURUM SONU:** Kaydet → MEMORY.md + DURUM_OZETI.md güncelle → TERMINOLOJI.md + DERSLER.md güncelle → git commit

## Üç Oturum Türü

**Okuma Oturumu** — PDF karmaşık veya uzunsa:
- Sadece PDF oku + `_notlar.md` yaz; yazıma geçilmez
- Context tamamen okumaya ayrılır

**Yazım Oturumu** — Notlar hazırsa:
- `_notlar.md` oku + tez metnini yaz; context tamamen yazıma ayrılır

**Tek Oturum** — Kısa bölümler için:
- Okuma + not + yazım aynı oturumda

## Yazım Sırasında Kaynak Keşfi

```
AI bir paragraf yazıyor → kaynak lazım → /sources/'da var mı?
  ├─ EVET → oku, sayfa bul, dipnot yaz, devam et
  └─ HAYIR → YAZIMI DURDUR
       → Kaynak bul ([[open-access-chain]] veya kullanıcıya sor)
       → Kaynak gelene kadar O PARAGRAFI YAZMA
       → [KAYNAK BEKLENİYOR: konu, önerilen kaynak] etiketi koy
       → Başka paragraftan devam et
```

[[iron-rules]] Kural 1: Asla kaynaksız cümle yazılmaz. Kaynak yoksa paragraf bekler.

## Her Tez Dosyasının Başında Metadata

```markdown
<!-- TEZ DOSYASI METAVERİSİ
Bölüm: [X]
Alt Bölüm: [X.Y]
Dosya: [dosya yolu]
Başlık: [alt bölüm başlığı]
Durum: [TAMAMLANDI / DEVAM EDECEK / TASLAK]
Son dipnot no: [X]
Kelime sayısı: [X]
Son güncelleme: [tarih]
Önceki bölüm: [dosya adı]
Sonraki bölüm: [dosya adı]
-->
```

## Dipnot Kuralları

- Tez genelinde sürekli numaralama (1, 2, 3... son dipnota kadar)
- Her dipnot PDF'ten doğrulanmış sayfa numarası içerir
- Ardışık aynı kaynakta "a.g.e." / "Ibid." kullanılır
- Format seçilen atıf sistemine göre

## Agent Desteği / Agent Support

**Style Linter** — Her bölüm tamamlandığında pasif ses yoğunluğu, aşırı hedge zincirleri ve abartılı iddia dili için otomatik tarama yapar.

Tetikleme: Bölüm yazımı bittikten sonra (bölüm başına en az 1 kez çalıştır).

```bash
python3 tools/style_linter.py <bolum_dosyasi.md> --lang tr --json
```

Sonuç yorumu:
- `passive_density > 0.25` → pasif cümleleri listele, kullanıcıdan etken forma çevirmesini iste
- `overhedge_count > 0` → zincirleri göster ("görülmektedir ki bu şekilde olduğu düşünülebilir")
- `overclaim_count > 0` → abartılı iddiaları işaretle ("kesinlikle kanıtlamaktadır")

---

**Citation Verifier** — Her paragraftaki iddiaları kaynak PDF'leriyle çapraz doğrular.

Tetikleme: Kullanıcı A/B/C seçimini yaptıktan sonra, bölüm tamamlandığında (toplu) veya Faz 7 geçiş kapısı öncesi (zorunlu).

```bash
python3 agents/run.py citation_verifier \
  --claim "[İddia metni ve atıf]" \
  --source "sources/[DOSYA.pdf]"
```

Sonuç yorumu:
- `confirmed` → yeşil, devam
- `partial` → kullanıcıya ilgili alıntıyı göster, iddiayı daraltmayı sor
- `not_found` → Demir Kural 1 ihlali adayı, yeniden yaz veya kaldır
- `contradicted` → kritik, zorunlu yeniden yazım

**Methodology Checker** — Tezprotokol.md tamamlandıktan sonra Faz 5'te bir kez çalıştırılır. Detay: [[agent-orchestration]].

---

## AI Hakem İncelemesi / Faz 7 Geçiş Kapısı

İlk 2-3 bölüm yazıldıktan sonra AI Hakem İncelemesi tetiklenir (bkz. `reviewer-mode.md`).
Danışmanı olan kullanıcılar bu noktada bölümleri danışmanlarına da gösterebilir.
Geri bildirim DERSLER.md'ye kaydedilir.
