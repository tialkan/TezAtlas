---
title: "Onboarding — Document Type & Language Selection"
node_type: onboarding
priority: critical
tags: [onboarding, setup, document-type, language, resume]
links_to:
  - skills/core/operating-modes.md
  - skills/core/session-continuity.md
  - skills/core/status-command.md
language: bilingual
version: "3.0"
---

# Onboarding — Document Type & Language Selection

This is the first node loaded when the `/tezatlas` command runs.
Resolve all seven items before phase work begins. Infer first, ask only what is missing (STEP 0.5).
Iron Rules apply from this moment forward, regardless of document type or language.

---

## STEP 0 — New Project or Resume? / Yeni Proje mi, Devam mı?

**Before asking any questions, check for an existing project:**

```
Does STATUS.md exist in the working directory?
  YES → Load STATUS.md → Present recovery banner → Offer A/B/C:
         A) Resume from last position (recommended)
         B) Review STATUS.md before resuming
         C) Start a new project
  NO  → Proceed to STEP 0.5 below
```

**Recovery banner (if STATUS.md found):**
```
╔══════════════════════════════════════════════════════╗
║  RESUMING: [Project Name]                            ║
║  Last session: [DATE] ([N days ago])                 ║
║  Phase: [Phase Name + Number] ([X]% complete)       ║
║  Next action: [ACTION 1 from STATUS.md]              ║
║  Blockers: [N] | Open questions: [N]                 ║
╚══════════════════════════════════════════════════════╝
→ Type A to resume, B to review, or C for new project
```

**Also available at any time:** `/status` — read-only 5-line project summary (no session init)

---

## STEP 0.5 — Infer Before Asking / Sormadan Önce Çıkar

Follow `skills/ux/question-protocol.md`. The seven questions below are a checklist,
not a script. Fill each item from the user's words and the files in the folder first.

| Item | Infer from | Default if nothing found |
|---|---|---|
| 1. Document type | User's words ("tez", "makale", "bildiri", "proje önerisi"), file names, templates | Ask (no default) |
| 2. Language | Language of the user's messages, language of drafts in the folder | The language the user writes in |
| 3. Field | User's words, source titles in `sources/`, journal/template names | Ask, offering the 2-3 closest fields as options |
| 4. Mode | — | A) Research Copilot |
| 5. Researcher type | User's words ("danışmanım", "hocam", "supervisor") | A) With advisor if mentioned, else B) Independent |
| 6. Writing style | Existing drafts in the folder → analyze automatically | C) Set up during first writing session |
| 7. Output format | `.tex` → LaTeX, `.docx` → Word, a university template → its format | A) LaTeX for thesis/article, C) Word for report and grant |

Then show **one** summary and ask only what is still missing:

```
Anladıklarım:
- Belge türü: Yüksek lisans tezi (ilk mesajından)
- Dil: Türkçe (mesajlarından)
- Alan: Hukuk (kaynak başlıklarından)
- Mod: Araştırma yardımcısı (varsayılan)
- Danışman: Var (mesajından)
- Yazım üslubu: Klasördeki iki taslaktan çıkaracağım
- Çıktı: LaTeX, YÖK şablonu (varsayılan)

Bir yanlış varsa numarasını ve doğrusunu yaz. Doğruysa "tamam" de.
```

Ask a question from the list below only for items still unknown. Each question keeps
its option list, the recommended option first, and "write your own" last.
A user who says "you decide" / "sen seç" gets the defaults above.

---

---

## EN — English

Welcome to TezAtlas.

Before we begin, I need six pieces of information. Your answers determine which
phase sequence we follow, which language we work in, how terminology is adapted
to your discipline, which oversight mode is active, and how your writing voice
is preserved.

---

### Question 1 — Document Type

Which type of academic output are you producing?

```
A) Doctoral / Master's Thesis        (8 phases)
B) Journal Article                   (6 phases)
C) Conference Paper                  (5 phases)
D) Literature / Systematic Review    (6 phases)
E) Research Report                   (5 phases)
F) Book Chapter                      (5 phases)
G) Grant Proposal                    (6 phases)
H) Research Proposal / Prospectus    (5 phases)
```

Type the letter (A–H) or the full name.

---

### Question 2 — Writing Language

What language will you write in?

```
1) Turkish   (Türkçe)
2) English
3) German    (Deutsch)
4) French    (Français)
5) Spanish   (Español)
6) Other — please specify
```

Note: TezAtlas will respond, guide, and generate output in the language you choose.
Academic terminology will be adapted to the conventions of that language.

---

### Question 3 — Research Field

What is your research field or discipline?

Suggestions (type the number or free text):
```
1)  Law / Legal Studies
2)  Economics / Finance
3)  Medicine / Health Sciences
4)  Engineering / Technology
5)  Social Sciences (Sociology, Political Science, Anthropology, ...)
6)  Humanities (History, Literature, Philosophy, ...)
7)  Natural Sciences (Biology, Chemistry, Physics, ...)
8)  Computer Science / Informatics
9)  Education
10) Other — please describe
```

Your field helps TezAtlas adapt citation conventions, terminology,
and phase emphasis (e.g., quantitative vs. qualitative methodology nodes).

---

## Question 4 — Operating Mode / Çalışma Modu

**EN:**

> **How would you like TezAtlas to work with you?**
>
> **A) Research Copilot — Guided Writing** *(Recommended)*
> TezAtlas drafts A/B options for every section from your notes and sources. You choose, merge, or redirect. An Academic Writing Note explains the reasoning behind each option. Core intellectual tasks (thesis argument, data interpretation, conclusions) are always yours — never AI-generated.
> ✅ Faster output | Overcomes blank-page paralysis | Teaches through examples
> 🌟 Speed: ★★★★☆ | AI involvement: ★★★★☆ | Editorial control: ★★★★★
>
> **B) Thought Partner — You Write**
> You write every word. TezAtlas asks sharp questions, flags gaps, checks sources, and guides your thinking — but never drafts.
> ✅ Full authorial control | No AI text in your document
> 🌟 Speed: ★★☆☆☆ | AI involvement: ★★☆☆☆ | Editorial control: ★★★★★
>
> **Not sure?** Choose A. You can switch task-by-task with `/mode assistant` at any time.
>
> **Decision Guide:**
> → Blank-page anxiety or first academic work? → A (Copilot writes, you choose)
> → Tight deadline (< 4 weeks)? → A (faster output)
> → Want to learn by doing, not selecting? → B (you write, AI coaches)
> → Don't trust AI-generated text? → B (full authorial control)
> → Not sure at all? → A (you can switch anytime with `/mode assistant`)

**TR:**

> **TezAtlas sizinle nasıl çalışsın?**
>
> **A) Araştırma Yardımcısı — Rehberli Yazım** *(Önerilen)*
> TezAtlas notlarınızdan ve kaynaklarınızdan her bölüm için A/B seçenekleri üretir. Siz seçer, birleştirir veya yeniden yönlendirirsiniz. Her seçenek setinin sonunda Akademik Yazım Notu yapıyı açıklar. Temel entelektüel görevler (tez argümanı, veri yorumu, sonuçlar) her zaman size aittir.
> ✅ Daha hızlı çıktı | Boş sayfa felcini kırar | Örneklerle öğretir
> 🌟 Hız: ★★★★☆ | AI müdahalesi: ★★★★☆ | Editoryal kontrol: ★★★★★
>
> **B) Düşünce Ortağı — Siz Yazın**
> Her kelimeyi siz yazarsınız. TezAtlas keskin sorular sorar, boşlukları işaretler, kaynakları kontrol eder — ama taslak üretmez.
> ✅ Tam yazarlık kontrolü | Belgenizde AI metni yok
> 🌟 Hız: ★★☆☆☆ | AI müdahalesi: ★★☆☆☆ | Editoryal kontrol: ★★★★★
>
> **Emin değilseniz?** A'yı seçin. İstediğiniz zaman `/mode assistant` ile geçiş yapabilirsiniz.

---

### Question 5 — Researcher Type (Advisor / Reviewer Mode)

Do you have an institutional advisor or supervisor for this work?

```
A) Yes — I have an advisor / supervisor
   → AI Peer Review + show to advisor: Hybrid Mode
     Claude runs AI review first, then you bring clean work to advisor

B) No — Independent researcher / professional / post-doc
   → AI Peer Review only: Claude runs structured challenge sessions
     as a Senior Peer Reviewer at every phase gate (see: reviewer-mode.md)

C) Limited — I have an advisor but access is infrequent (monthly or less)
   → Hybrid Mode: Claude pre-screens, you bring clean work to advisor
```

> In all cases, Claude runs AI Peer Review at every phase gate.
> Human advisor review is additive — it strengthens the process.
> See [[core/reviewer-mode]] for full protocol.

---

### Question 6 — Writing Style Profile (Natural Voice)

TezAtlas ensures AI-assisted text matches your personal writing voice. How would you like to set up your writing profile?

```
A) Analyze my sample — I'll paste 2-3 pages of my previous academic writing
   → TezAtlas analyzes your sentence length, punctuation habits, paragraph
     style, and structural preferences automatically

B) Quick questions — Ask me about my preferences
   → 7 short questions about your writing habits

C) Skip for now — I'll set it up during the first writing session
```

> Your profile is saved to `YAZIM_PROFILI.md` and used during Draft Generator mode
> to keep AI output consistent with your voice. See: `natural-voice.md`

---

### Question 7 — Output Format

What format will your final document be in?

```
A) LaTeX → PDF    (Recommended for thesis and journal articles)
   → TezAtlas produces LaTeX-ready Markdown drafts
   → /latex converts to .tex, /compile-pdf compiles to PDF
   → Templates: YÖK thesis, APA7, IEEE, Chicago, ACM

B) Markdown only  (Simple — readable in any editor)
   → No compilation step needed
   → Good for early drafts and reports

C) Word (.docx)   (For institutional submission requirements)
   → Markdown drafts, manual paste to Word
   → /submission-check reminds you of formatting steps

D) Both A + B     (LaTeX primary, Markdown backup)
```

> Your choice is saved to `STATUS.md → output_format` and used by `/latex` and `/compile-pdf`.
> You can change it at any time by editing STATUS.md.

---

### Routing — After Your Answers

Once you answer all seven questions, TezAtlas will:

1. Confirm your selections with a banner (including active mode)
2. Determine User Type: Student Mode or Researcher Mode (see `operating-modes.md`)
3. Route you to the correct Phase 0 node:

| Choice | Phase 0 Node |
|--------|-------------|
| A — Thesis | `skills/phases/thesis/phase-0-identity.md` |
| B — Journal Article | `skills/phases/article/phase-0-claim.md` |
| C — Conference Paper | `skills/phases/conference/phase-0-abstract.md` |
| D — Lit / Systematic Review | `skills/phases/lit-review/phase-0-protocol.md` |
| E — Research Report | `skills/phases/report/phase-0-brief.md` |
| F — Book Chapter | `skills/phases/book-chapter/phase-0-alignment.md` |
| G — Grant Proposal | `skills/phases/grant-proposal/phase-0-brief.md` |
| H — Research Proposal | `skills/phases/research-proposal/phase-0-prospectus.md` |

4. Set context mode (Student / Researcher) and writing mode (Copilot default for all)
5. Load the Iron Rules + Anti-Hallucination Protocol as background context (always active)
6. Begin Phase 0 guided work in your chosen language
7. Create STATUS.md and DASHBOARD.md at first session end (includes output_format and word targets)

---

## TR — Türkçe

TezAtlas'a hoş geldiniz.

Başlamadan önce altı bilgiye ihtiyacım var. Cevaplarınız hangi aşama dizisini
takip edeceğimizi, hangi dilde çalışacağımızı, terminolojinin disiplininize
nasıl uyarlanacağını, hangi denetim modunun aktif olacağını ve yazım sesinizin
nasıl korunacağını belirler.

---

### Soru 1 — Belge Türü

Hangi tür akademik çıktı üretiyorsunuz?

```
A) Doktora / Yüksek Lisans Tezi      (8 aşama)
B) Dergi Makalesi                    (6 aşama)
C) Konferans Bildirisi               (5 aşama)
D) Literatür / Sistematik Derleme    (6 aşama)
E) Araştırma Raporu                  (5 aşama)
F) Kitap Bölümü                      (5 aşama)
G) Hibe Teklifi / Grant Proposal     (6 aşama)
H) Araştırma Önerisi / Prospektüs    (5 aşama)
```

Harf (A–H) veya tam adı yazın.

---

### Soru 2 — Yazım Dili

Hangi dilde yazacaksınız?

```
1) Türkçe
2) İngilizce   (English)
3) Almanca     (Deutsch)
4) Fransızca   (Français)
5) İspanyolca  (Español)
6) Diğer — lütfen belirtin
```

Not: TezAtlas seçtiğiniz dilde yanıt verir, yönlendirir ve çıktı üretir.
Akademik terminoloji o dilin kurallarına uyarlanır.

---

### Soru 3 — Araştırma Alanı

Araştırma alanınız veya disiplininiz nedir?

Öneriler (numara veya serbest metin yazın):
```
1)  Hukuk
2)  Ekonomi / Finans
3)  Tıp / Sağlık Bilimleri
4)  Mühendislik / Teknoloji
5)  Sosyal Bilimler (Sosyoloji, Siyaset Bilimi, Antropoloji, ...)
6)  İnsani Bilimler (Tarih, Edebiyat, Felsefe, ...)
7)  Doğa Bilimleri (Biyoloji, Kimya, Fizik, ...)
8)  Bilgisayar Bilimi / Bilişim
9)  Eğitim
10) Diğer — lütfen açıklayın
```

---

---

### Soru 4 — Çalışma Modu

**TR:**

> **TezAtlas sizinle nasıl çalışsın?**
>
> **A) Araştırma Yardımcısı — Rehberli Yazım** *(Önerilen)*
> TezAtlas notlarınızdan ve kaynaklarınızdan her bölüm için A/B seçenekleri üretir. Siz seçer, birleştirir veya yeniden yönlendirirsiniz. Her seçenek setinin sonunda Akademik Yazım Notu yapıyı ve kaynak öğrenimini açıklar. Temel entelektüel görevler (tez argümanı, veri yorumu, sonuçlar) her zaman size aittir.
> ✅ Daha hızlı çıktı | Boş sayfa felcini kırar | Örneklerle öğretir
> 🌟 Hız: ★★★★☆ | AI müdahalesi: ★★★★☆ | Editoryal kontrol: ★★★★★
>
> **B) Düşünce Ortağı — Siz Yazın**
> Her kelimeyi siz yazarsınız. TezAtlas keskin sorular sorar, boşlukları işaretler, kaynakları kontrol eder — ama taslak üretmez.
> ✅ Tam yazarlık kontrolü | Belgenizde AI metni yok
> 🌟 Hız: ★★☆☆☆ | AI müdahalesi: ★★☆☆☆
>
> **Emin değilseniz?** A'yı seçin. İstediğiniz zaman `/mode assistant` ile geçiş yapabilirsiniz.
>
> **Karar Rehberi:**
> → Boş sayfa korkusu veya ilk akademik çalışma? → A (AI yazar, siz seçersiniz)
> → Sıkı teslim tarihi (< 4 hafta)? → A (daha hızlı çıktı)
> → Yaparak öğrenmek istiyorsanız? → B (siz yazarsınız, AI koçluk yapar)
> → AI metnine güvenmiyorsanız? → B (tam yazarlık kontrolü)
> → Hiç emin değilseniz? → A (istediğiniz zaman `/mode assistant` ile geçiş yapabilirsiniz)

---

### Soru 5 — Araştırmacı Tipi (Danışman / Hakem Modu)

Bu çalışma için kurumsal bir danışmanınız veya tez yöneticiniz var mı?

```
A) Evet — Danışmanım / tez yöneticim var
   → AI Hakem İncelemesi + danışmana da göster: Hibrit Mod
     Claude önce AI incelemesi yapar, siz temizlenmiş çalışmayla danışmana gidersiniz

B) Hayır — Bağımsız araştırmacı / profesyonel / post-doktora
   → Yalnızca AI Hakem İncelemesi: Claude her faz kapısında Kıdemli Hakem rolüyle
     yapılandırılmış sorgulama oturumu yürütür (bkz: reviewer-mode.md)

C) Kısıtlı — Danışmanım var ama erişimim sınırlı (ayda bir veya daha az)
   → Hibrit Mod: Claude önce tarar, siz temizlenmiş çalışmayla danışmana gidersiniz
```

> Her durumda Claude, her faz kapısında AI Hakem İncelemesi yapar.
> İnsan danışman incelemesi buna eklenir — süreci güçlendirir.
> Tam protokol için bkz. [[core/reviewer-mode]].

---

### Soru 6 — Yazım Stili Profili (Doğal Ses)

TezAtlas, YZ destekli metnin sizin kişisel yazım sesinize uymasını sağlar. Yazım profilinizi nasıl oluşturmak istersiniz?

```
A) Örneğimi analiz et — Daha önce yazdığım 2-3 sayfa akademik metni yapıştıracağım
   → TezAtlas cümle uzunluğunuzu, noktalama alışkanlıklarınızı, paragraf
     stilinizi ve yapısal tercihlerinizi otomatik analiz eder

B) Hızlı sorular — Tercihlerimi sor
   → Yazma alışkanlıklarınız hakkında 7 kısa soru

C) Şimdilik geç — İlk yazım oturumunda kurarım
```

> Profiliniz `YAZIM_PROFILI.md`'ye kaydedilir ve Taslak Üretici modunda
> YZ çıktısının sesinizle tutarlı kalmasını sağlar. Bkz: `natural-voice.md`

---

### Soru 7 — Çıktı Formatı

Son belgeniz hangi formatta olacak?

```
A) LaTeX → PDF    (Tez ve dergi makaleleri için önerilen)
   → TezAtlas LaTeX uyumlu Markdown taslaklar üretir
   → /latex .tex'e dönüştürür, /compile-pdf PDF'e derler
   → Şablonlar: YÖK tezi, APA7, IEEE, Chicago, ACM

B) Yalnızca Markdown  (Basit — her editörde okunur)
   → Derleme adımı gerekmez
   → Erken taslaklar ve raporlar için uygun

C) Word (.docx)   (Kurumsal teslim gereksinimleri için)
   → Markdown taslaklar, Word'e manuel yapıştırma
   → /submission-check biçimlendirme adımlarını hatırlatır

D) A + B birlikte (LaTeX birincil, Markdown yedek)
```

> Seçiminiz `STATUS.md → output_format` alanına kaydedilir ve `/latex`, `/compile-pdf` tarafından kullanılır.
> STATUS.md'yi düzenleyerek istediğiniz zaman değiştirebilirsiniz.

---

### Yönlendirme — Cevaplarınızdan Sonra

Yedi soruyu yanıtladıktan sonra TezAtlas:

1. Seçimlerinizi aktif mod dahil bir banner ile onaylar
2. Kullanıcı tipini belirler: Öğrenci Modu veya Araştırmacı Modu (`operating-modes.md`)
3. Sizi doğru Aşama 0 düğümüne yönlendirir
4. Demir Kuralları + Anti-Halüsinasyon Protokolü'nü arka planda yükler (her zaman aktif)
5. Seçtiğiniz dilde Aşama 0'a başlar
6. İlk oturum sonunda STATUS.md ve DASHBOARD.md oluşturur (output_format ve kelime hedefleri dahil)
