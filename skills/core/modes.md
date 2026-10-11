---
title: "Operating Modes (superseded, see operating-modes.md)"
title_tr: "Çalışma Modları (eski, bkz. operating-modes.md)"
node_type: foundation
priority: critical
description: "TezAtlas operates in two modes. Thought Partner (default): AI guides, questions, and checks while the user writes. Draft Generator: AI produces drafts from user's notes; user must critically review and own the output. Mode is chosen per task, with smart defaults based on user type and phase."
tags: [modes, thought-partner, draft-generator, academic-integrity, SRL]
links_to:
  - skills/core/iron-rules.md
  - skills/core/writing-psychology.md
  - skills/core/academic-integrity.md
  - skills/core/onboarding.md
language: bilingual
version: "2.0"
superseded_by: skills/core/operating-modes.md
---

# Çalışma Modları (eski düğüm) / Operating Modes (superseded)

> **Bu düğüm artık geçerli değil.** Kanonik tanım: [[operating-modes]].
> This node is superseded. The canonical definition is [[operating-modes]].

Önceki sürümde burada "Düşünce Ortağı varsayılan, Taslak Üretici kilitli ve kademeli açılır" kuralı yazıyordu. Bu kural `operating-modes.md`, `CLAUDE.md` ve onboarding ile çelişiyordu ve kaldırıldı. Geçerli kurallar:

- Varsayılan mod **Araştırma Yardımcısı (Research Copilot / Rehberli Yazım)**: yapay zekâ bölüm ve paragraf için A/B taslak seçenekleri sunar, kullanıcı seçer, birleştirir ya da yönlendirir.
- **Düşünce Ortağı (Thought Partner / İş Akışı Asistanı)**: kullanıcı her kelimeyi kendisi yazar; yapay zekâ yönlendirir, sorar, denetler. Geçiş: `/mode assistant`, geri dönüş: `/mode copilot`.
- Her iki modda da tezin ana iddiası, veri yorumu ve sonuçlar yapay zekâ tarafından üretilmez.
- Kaynaksız taslak üretilmez; kaynak bekleyen yer `[KAYNAK BEKLENİYOR]` diye işaretlenir.

Ayrıntılar, görev türü ayrımı ve mod göstergeleri için [[operating-modes]]; Rehberli Yazım'ın işleyişi için [[guided-writing-mode]]; Öğrenci/Araştırmacı kullanıcı türleri için [[user-modes]].
