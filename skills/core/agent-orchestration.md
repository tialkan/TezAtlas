---
title: "Agent Orchestration — Claude Code Playbook"
title_tr: "Agent Orkestrasyonu — Claude Code Oyun Kitabı"
node_type: core
description: "Defines WHEN and HOW Claude Code invokes the three specialist agents (Source Hunter, Methodology Checker, Citation Verifier) during a TezAtlas session. Python bridge is the execution layer; Claude Code is the orchestrator."
description_tr: "TezAtlas oturumu sırasında Claude Code'un üç uzman agent'ı (Source Hunter, Methodology Checker, Citation Verifier) ne zaman ve nasıl çağıracağını tanımlar. Python bridge yürütme katmanı; Claude Code orkestratördür."
tags: [core, agents, orchestration, multi-agent, source-hunter, methodology-checker, citation-verifier]
links_to:
  - skills/core/iron-rules.md
  - skills/core/anti-hallucination.md
language: bilingual
version: "1.0"
---

# Agent Orchestration — Claude Code Playbook
# Agent Orkestrasyonu — Claude Code Oyun Kitabı

## Overview / Genel Bakış

**EN:** TezAtlas uses a hybrid multi-agent architecture. Claude Code is the primary orchestrator and never loses the conversation thread. The Python bridge (`agents/run.py`) dispatches tasks to external LLM providers (Gemini, DeepSeek, Grok, Ollama, etc.) for computationally independent tasks — source discovery, methodology validation, citation verification.

**TR:** TezAtlas hibrit çok-agent mimarisi kullanır. Claude Code birincil orkestratördür ve konuşma bağlamını asla kaybetmez. Python bridge (`agents/run.py`), kaynaktan bağımsız görevler için — kaynak keşfi, metodoloji doğrulama, atıf doğrulama — harici LLM sağlayıcılara görev dağıtır.

---

## Prerequisites / Ön Koşullar

Before invoking any agent, verify setup:

```bash
# Check provider configuration
python3 agents/run.py --list-providers

# Health check (sends minimal prompt to each configured provider)
python3 agents/run.py --test-providers
```

**If `.env` is missing or provider is unconfigured:**
- Inform the user: "Agent [name] requires [PROVIDER_API_KEY] in `.env`. Falling back to manual workflow."
- Continue without the agent — all workflows function without agents.
- Agents are acceleration tools, not hard dependencies.

**TR:** `.env` yoksa veya sağlayıcı yapılandırılmamışsa kullanıcıyı bildir ve agent olmadan devam et.

---

## Agent Trigger Map / Agent Tetikleme Haritası

| Agent | Phase | Trigger Condition | Who invokes |
|-------|-------|-------------------|-------------|
| **Source Hunter** | Phase 2 (any doc type) | sources/ count < minimum OR user asks for recommendations | Claude Code (foreground) |
| **Source Hunter** | Phase 3 reading | Saturation not reached, deferred pool needs expansion | Claude Code (background) |
| **Methodology Checker** | Phase 3-5 (thesis/article) | Methodology section drafted or substantially revised | Claude Code (foreground) |
| **Methodology Checker** | Any writing phase | User changes research design mid-project | Claude Code (foreground) |
| **Citation Verifier** | Phase 6-7 writing | After each complete paragraph with sourced claims | Claude Code (background) |
| **Citation Verifier** | Final gate check | Before phase gate to finalization/submission | Claude Code (foreground) |

---

## Command Templates / Komut Şablonları

### Source Hunter

```bash
# Foreground — waits for results before proceeding
python3 agents/run.py source_hunter \
  --research-question "[RESEARCH_QUESTION from STATUS.md]" \
  --field "[FIELD from STATUS.md]" \
  --existing-sources sources/ \
  --language [tr|en|both]

# After completion: results in KAYNAK_ONERILERI.md (auto-created by agent)
```

**When to call (foreground):**
- Phase 2 start: sources/ is empty or has fewer than minimum
- User asks: "Yeni kaynak öner" / "Find more sources"

**When to call (background — use Bash `&` flag or run_in_background):**
- During Phase 3 reading when user is working: run in background, report results at session end

---

### Methodology Checker

```bash
python3 agents/run.py methodology_checker \
  --input [methodology_section.md OR chapter_X_methodology.md] \
  --research-question "[RESEARCH_QUESTION]" \
  --field "[FIELD]" \
  --document-type [thesis|article|grant-proposal|report]

# After completion: assessment in METODOLOJI_DEGERLENDIRME.md (auto-created)
```

**When to call:**
- After user completes methodology section draft
- After significant structural changes to methodology
- At Phase 5 gate (thesis), Phase 3 gate (article), Phase 3 gate (grant-proposal)

**Output interpretation:**
- `alignment_score >= 80`: Pass — mention score, highlight top 2 recommendations
- `alignment_score 60-79`: Warning — show bias_warnings[], block phase gate until addressed
- `alignment_score < 60`: Hard stop — show all issues, return to methodology phase

**Anti-Hallucination Rule (Iron Rule M):**
All recommendations in the Methodology Checker output must cite a source.
If `recommendations[]` items lack source citations, tag them `[Source: Unverified]`
before presenting to user. See `anti-hallucination.md`.

---

### Citation Verifier

```bash
python3 agents/run.py citation_verifier \
  --claim "[EXACT CLAIM TEXT with citation]" \
  --source "sources/[FILENAME.pdf]"

# Returns: verification_status, relevant_quotes[], confidence
```

**When to call:**
- Per paragraph: after each paragraph is drafted and accepted (A/B/C selection made)
- Per section: batch verify all claims in a completed section before moving on
- Pre-finalization: run on entire draft before Phase 7/submission gate

**Output interpretation:**
- `confirmed`: Green. Include relevant_quotes in notes for reproducibility.
- `partial`: Yellow. Show user the relevant_quotes, ask if the claim needs narrowing.
- `not_found`: Red. Iron Rule 1 violation candidate — claim must be rewritten or removed.
- `contradicted`: Critical — source says the opposite. Mandatory rewrite.

---

## Result Integration Protocol / Sonuç Entegrasyon Protokolü

**EN:** Agent outputs are JSON. Claude Code reads the output file, interprets it, and integrates into the session. Never paste raw JSON to the user.

**TR:** Agent çıktıları JSON formatındadır. Claude Code çıktı dosyasını okur, yorumlar ve oturuma entegre eder. Ham JSON'u kullanıcıya asla gösterme.

### Output Files

| Agent | Output File | Content |
|-------|-------------|---------|
| Source Hunter | `KAYNAK_ONERILERI.md` | Recommended sources with relevance scores |
| Methodology Checker | `METODOLOJI_DEGERLENDIRME.md` | Alignment score, warnings, recommendations |
| Citation Verifier | `DOGRULAMA_RAPORU.md` | Per-claim verification status and quotes |

### Presentation Rules

**Source Hunter results:**
1. Group by relevance score (High/Medium)
2. For each source: title, authors, year, DOI/URL, 1-sentence relevance rationale
3. Ask user: "Hangilerini indireyim?" (Which should I download?)
4. Proceed to download approved sources via existing Iron Rule 3 protocol

**Methodology Checker results:**
1. Lead with the score: "Metodoloji uyum skoru: [X]/100"
2. List bias_warnings[] as actionable items, not just warnings
3. For each warning: explain WHY it matters for this specific research
4. Let user decide on recommended changes — never impose

**Citation Verifier results:**
1. Confirmed claims: brief acknowledgment, move on
2. Partial/not_found: show the specific quote gap, present rewrite options
3. Contradicted: flag as Iron Rule 1 violation, mandatory action required

---

## Per-Document-Type Integration / Belge Türüne Göre Entegrasyon

### Thesis (skills/phases/thesis/)

```
Phase 2 → Source Hunter (Phase 2 start, foreground)
Phase 3 → Source Hunter (background during reading if saturation < 80%)
Phase 5 → Methodology Checker (after tezprotokol.md finalized)
Phase 6 → Citation Verifier (per paragraph, can run background)
Phase 7 → Citation Verifier final pass (foreground, required for gate)
```

### Article (skills/phases/article/)

```
Phase 1 (Literature) → Source Hunter
Phase 3 (Writing — Methodology section) → Methodology Checker
Phase 4 (Writing) → Citation Verifier (per section)
Phase 6 (Peer Review Revision) → Citation Verifier (on revised claims)
```

### Grant Proposal (skills/phases/grant-proposal/)

```
Phase 1 (Funder Analysis) → Source Hunter
Phase 3 (Budget/Methodology) → Methodology Checker
Phase 4 (Writing) → Citation Verifier (every factual claim)
```

### Literature Review (skills/phases/lit-review/)

```
Phase 1-2 (Search/Screen) → Source Hunter (expand search)
Phase 4 (Synthesis) → Methodology Checker (protocol compliance)
Phase 5 (Writing) → Citation Verifier (per finding reported)
```

### Report (skills/phases/report/)

```
Phase 2 (Evidence) → Source Hunter
Phase 3 (Analysis) → Methodology Checker
Phase 4 (Writing) → Citation Verifier (all factual claims)
```

### Conference (skills/phases/conference/)

```
Phase 1 → Source Hunter
Phase 3 (Writing) → Citation Verifier
```

### Book Chapter (skills/phases/book-chapter/)

```
Phase 1-2 → Source Hunter
Phase 4 (Writing) → Citation Verifier
```

### Research Proposal (skills/phases/research-proposal/)

```
Phase 2 → Source Hunter
Phase 3 (Methodology) → Methodology Checker
```

---

## Failure & Fallback / Hata ve Geri Dönüş

```
Agent call fails → Log error → Continue without agent
Provider not configured → Inform user → Proceed with manual workflow
Timeout (>60s) → Kill process → Report timeout → Proceed manually
Invalid JSON output → Retry once → If fails: show raw output + ask user to interpret
```

**Hard rule:** Agent failures NEVER block the research workflow. All Iron Rules, phase gates, and Iron Rule 1 source verification apply regardless of agent availability.

**TR:** Agent hataları araştırma iş akışını asla engellemez. Tüm Demir Kurallar, agent mevcut olmasa da geçerliliğini korur.

---

## Invocation Examples / Çağrı Örnekleri

### Scenario 1: Phase 2 — New Project, Empty sources/

```
User starts Phase 2 with empty sources/
→ Claude Code reads STATUS.md for research_question and field
→ Claude Code calls: python3 agents/run.py source_hunter --research-question "..." --field economics --existing-sources sources/ --language both
→ Reads KAYNAK_ONERILERI.md
→ Presents grouped recommendations to user
→ Downloads approved sources
```

### Scenario 2: Phase 6 — Citation Verification During Writing

```
User accepts paragraph B from drafting alternatives
→ Claude Code identifies all claims with citations in paragraph
→ For each claim: python3 agents/run.py citation_verifier --claim "..." --source sources/file.pdf
→ Aggregates results
→ If all confirmed: proceed
→ If any not_found: flag before moving to next paragraph
```

### Scenario 3: Phase 5 — Methodology Check

```
User finalizes tezprotokol.md
→ Claude Code calls: python3 agents/run.py methodology_checker --input tezprotokol.md --research-question "..." --field ... --document-type thesis
→ Reads METODOLOJI_DEGERLENDIRME.md
→ Presents score and actionable warnings
→ If score < 80: phase gate does not open until user addresses warnings
```

---

## Bağımsız denetim: yazar ve denetçi ayrı modeller / Independent review

Taslağı yazan model kendi hatasını zor görür. Yazım aşamalarında her bölüm bittiğinde ve aşama kapısından önce taslak, yazardan farklı şirketlerin modelleriyle denetlenir:

- Claude Code içinde: `/cross-review <bölüm dosyası>`
- Komut satırında: `tezatlas-agents capraz_denetim --input <bölüm dosyası>` (tek model için `denetci`, dergi hakemi provası için `hakem`)

Denetçi yazarın gerekçelerini görmez; yalnız taslağı ve `notes/` / `notlar/` klasöründeki kaynak notlarını okur. Rapor ortak bulguları önce, yalnız bir modelin bulduklarını sonra gösterir; her bulguda kararı kullanıcı verir ve rapora yazar. Ayrıntı ve maliyet: `docs/coklu-model.md`.
