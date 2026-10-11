---
title: "tezatlas.com — BYOK Web Version Roadmap"
title_tr: "tezatlas.com — BYOK Web Versiyon Yol Haritası"
node_type: core
description: "Phased roadmap for tezatlas.com: Phase 1 static docs site, Phase 2 BYOK Claude API integration with localStorage/Supabase, Phase 3 collaborative features, Phase 4 Exchange marketplace."
description_tr: "tezatlas.com için aşamalı yol haritası: Faz 1 statik dokümantasyon sitesi, Faz 2 BYOK Claude API entegrasyonu (localStorage/Supabase), Faz 3 işbirlikçi özellikler, Faz 4 Exchange pazaryeri."
tags: [core, web-version, byok, roadmap, tezatlas-com, nextjs, supabase, claude-api]
links_to:
  - skills/core/tezatlas-exchange.md
  - skills/core/plugin-system.md
  - skills/core/data-privacy.md
language: bilingual
version: "1.0"
---

# tezatlas.com — Web Versiyon Yol Haritası

> **Güncel karar belgesi:** `docs/saas-fizibilite.md` (Ekim 2026). Aşağıdaki ilk plan tarihî kayıttır; abonelik/BYOK, maliyet ve ilk ürün kapsamı için o belge geçerlidir. Kullanıcının Claude/ChatGPT aboneliği sitede kullanılamaz; site BYOK (OpenRouter) ve sınırlı ücretsiz pilotla çalışır.

## Mevcut Durum / Current State

TezAtlas şu an **Claude Code CLI** üzerinde çalışmaktadır:
- Yerel dosya sistemi (markdown)
- Claude Code'un araç seti (Bash, Read, Write, Glob vb.)
- Tek kullanıcı, tek oturum

`tezatlas.com` URL'si README'de geçmekte fakat henüz bir uygulama yoktur.

---

## Faz 1 — Statik Dokümantasyon Sitesi

**Hedef:** Yeni kullanıcılar TezAtlas'ı kolayca keşfedebilsin.

**Stack:** Astro veya Next.js (statik export)

**İçerik:**
- Skill grafiği görselleştirmesi (D3.js veya Mermaid)
- Faz akışları interaktif diyagram
- Kurulum rehberi (Claude Code + TezAtlas)
- Canlı demo (readonly, sabit veri ile)
- Desteklenen disiplinler ve belge türleri

**Hosting:** GitHub Pages veya Vercel (ücretsiz tier)
**Domain:** tezatlas.com (veya tezatlas.github.io başlangıç)

---

## Faz 2 — BYOK Web Uygulaması

**BYOK (Bring Your Own Key):** Kullanıcı kendi Claude API key'ini getirir → TezAtlas web üzerinde çalışır.

**Stack:**
```
Frontend:  Next.js 14+ App Router
AI:        Anthropic API (claude-sonnet-4-x veya claude-opus-4-x)
Storage:   localStorage (hızlı başlangıç) → Supabase (kalıcı)
Auth:      Supabase Auth (opsiyonel, anonim kullanım da mümkün)
```

**Temel özellikler:**
- Claude API key girişi (localStorage'da şifreli saklama)
- Faz yönetimi (mevcut TezAtlas akışı)
- Dosya yönetimi (tarayıcı tabanlı veya GitHub entegrasyonu)
- STATUS.md, READING_REPORT.md web arayüzü

**Gizlilik:** Kullanıcı verisi sunucuda saklanmaz — yalnızca localStorage veya kullanıcının seçtiği Supabase projesi.

---

## Faz 3 — İşbirlikçi Özellikler

**Hedef:** Danışman-öğrenci, ortak yazarlık iş akışları.

**Özellikler:**
- Danışman paylaşım linki: `tezatlas.com/review/[token]`
- Danışman yorumları Markdown formatında
- Faz geçiş onayı: danışman onaylamadan faz geçilmez
- Okuma notları paylaşımı (seçimli)
- Co-author iş akışı: bölüm bazlı sahiplik

**Stack eklentileri:**
- Supabase Realtime (canlı işbirliği)
- Row Level Security (kullanıcı verisi izolasyonu)

---

## Faz 4 — Exchange Entegrasyonu

**Bkz.:** `skills/core/tezatlas-exchange.md`

**Ek özellikler:**
- Exchange browse arayüzü (web)
- Tek tıkla paket kurulumu
- Paket yayınlama arayüzü
- Kullanıcı profili ve katkı geçmişi

---

## Teknik Notlar / Technical Notes

### API Güvenliği
```
BYOK modeli: API key tarayıcıda → direkt Anthropic API → yanıt tarayıcıya
Sunucu arası geçiş yok → key sunucuya ulaşmaz
```

### İstihdam Rehberi (Türkiye)
TÜBİTAK 1512 (girişimcilik) veya KOSGEB desteği ile web versiyonu için fon araştırması yapılabilir.

### Açık Kaynak Stratejisi
- Frontend: MIT lisansı
- Skill node'lar: CC BY 4.0
- Backend (Supabase yapılandırması): özel repo veya açık

---

## Zaman Çizelgesi (Tahmini)

| Faz | Süre | Ön Koşul |
|-----|------|----------|
| Faz 1 Docs | 2-4 hafta | Mevcut docs |
| Faz 2 BYOK | 6-8 hafta | Faz 1 tamamlı |
| Faz 3 Collab | 3-4 ay | Faz 2 + Supabase |
| Faz 4 Exchange | 2-3 ay | Faz 3 + Plugin API |

*Bunlar planlama tahminidir — kaynak ve önceliklere göre değişir.*
