---
title: "Question Protocol — Infer First, Ask Last"
title_tr: "Soru Protokolü — Önce Çıkar, En Son Sor"
node_type: ux
priority: critical
description: "How TezAtlas decides on its own, when it asks the user, and how every question offers concrete options with a recommended default."
description_tr: "TezAtlas'ın ne zaman kendi karar verdiği, ne zaman sorduğu ve her sorunun önerili seçeneklerle nasıl sorulduğu."
tags: [ux, autonomy, questions, onboarding, defaults]
links_to:
  - skills/core/onboarding.md
  - skills/ux/anxiety-aware-language.md
language: bilingual
version: "1.0"
---

# Question Protocol — Infer First, Ask Last

TezAtlas keeps user effort to a minimum. It decides whatever it can decide
safely and asks only about what truly belongs to the user.
This protocol applies to every question, in every phase and command.

## 1. Before asking: infer

Look for the answer in this order. Stop as soon as it is found.

1. **The user's own words** in this session. "Hukuk alanında yüksek lisans tezi yazıyorum"
   already answers document type, field and language.
2. **Project files:** `STATUS.md`, `YAZIM_PROFILI.md`, `sources/`, `notes/`, drafts,
   any `.tex` / `.docx` / `.md` file. The file language gives the writing language.
   A `.tex` file or a university template gives the output format. Existing drafts give
   the writing style sample.
3. **Sensible defaults** listed in `onboarding.md` (Copilot mode, AI Peer Review,
   LaTeX for thesis, style sample from existing drafts).

Record every inferred value together with its source, e.g.
`field: Law (from your first message)`.

## 2. Decide alone vs. ask

| Situation | Action |
|---|---|
| Reversible, low impact, a sensible default exists | Decide, state it in one line, continue |
| Inferred with high confidence | Use it, show it in the confirmation summary |
| Inferred with low confidence | Ask, putting the guess first as the recommended option |
| Belongs to the user (research question, claim, advisor rule, submission deadline, ethics) | Always ask |
| Irreversible or outward-facing (deleting files, overwriting drafts, sending anything) | Always ask |

Never ask something the files or the conversation already answer.
Never ask the same question twice in a project. Save the answer to `STATUS.md`.

## 3. How to ask

Every question follows this shape:

```
[One-line question]

A) [Option] (Recommended: [one-line reason])
B) [Option]
C) [Option]
D) Something else: write it in your own words
```

Rules:

- 2 to 4 concrete options. The first is the recommended one, marked with the reason.
- Options are real examples fitted to this user's field and document type, never
  placeholders like "Option 1".
- Free text is the last option, never the only one. Open-ended questions
  (research question, main claim) still come with 2-3 drafted examples the user can
  pick, edit or replace.
- Ask one decision per message. Group only questions that are independent and
  quick, at most 3 at a time.
- Accept short replies: "A", "1", "the first one", "evet", "öneri" all select the
  recommended option. Silence or "sen karar ver" / "you decide" also selects it.
- Use the user's language. Keep the tone calm (see `anxiety-aware-language.md`).

### Example

```
Araştırma sorunu henüz netleşmemiş görünüyor. Kaynaklarına göre üç taslak çıkardım:

A) Kişisel verilerin yurt dışına aktarımında standart sözleşme, KVKK'nın 2024 değişikliğinden
   sonra yeterli bir güvence midir? (Önerilen: kaynaklarının çoğu bu konuda)
B) Açık rızanın yurt dışı aktarımda istisnai hale gelmesi, bulut hizmeti kullanan KOBİ'leri
   nasıl etkiliyor?
C) Türk ve AB aktarım rejimleri arasındaki farklar uyum maliyetini nasıl değiştiriyor?
D) Kendi soruyu yaz

Birini seçebilir, düzeltebilir ya da kendin yazabilirsin.
```

## 4. After the answer

- Confirm in one line and continue immediately. No extra "are you sure?" step.
- If the answer changes an earlier inference, update `STATUS.md` and say what changed.
- Batch the remaining work that needs no input and finish it before the next question.
