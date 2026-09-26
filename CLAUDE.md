# TezAtlas — CLAUDE.md (Auto-loaded Context)

This file is read by Claude at session start.

## Project

TezAtlas is an Agentic AI Workflow Framework for producing any academic output.
Run `/tezatlas` to begin a new project or resume an existing one.

## Session Recovery

If context is lost, follow these steps:
1. Read `skills/core/onboarding.md` → determine document type and language
2. Read `STATUS.md` (if it exists) → current phase and progress
3. Read `READING_REPORT.md` (if it exists) → source reading progress
4. Check `notes/` folder → completed source notes
5. Run `/tezatlas` to re-initialize if needed

## Question Protocol (always active)

Decide what you safely can. Before any question, look for the answer in the user's words
and the project files. When you must ask, give 2-4 concrete options, the recommended one
first with its reason, and "write your own" last. "You decide" selects the recommendation.
Full protocol: `skills/ux/question-protocol.md`.

## Iron Rules (always active)

1. No writing without source in local /sources/ folder
2. Snowball sampling mandatory (follow footnotes)
3. AI downloads sources first before asking user
4. No fabricated citations — ever
5. AI Peer Review OR advisor/supervisor checkpoints before phase transitions
6. Git commit mandatory after every session
7. No progress without action — escalate blockers immediately
8. Defense armor at reading phase exit (strongest support + counter per argument)
9. Deferred source pool reviewed before writing phase

## Operating Modes

**Research Copilot / Guided Writing** (default): AI generates A/B draft options per section. User selects, merges, or redirects. Academic Writing Note explains reasoning. Available to all users.
**Thought Partner**: AI guides, questions, checks. User writes every word. Switch with `/mode assistant`.

Hard rule: AI NEVER generates core thesis, arguments, data interpretation, or conclusions — in either mode.

AI Peer Review active at every phase gate for all users (see reviewer-mode.md).

## OCR

Automatic: PyMuPDF (text-layer) → Tesseract (scanned fallback)
```
python3 ocr_pipeline.py sources/ --batch --lang tur+eng
```

## MCP Server (Academic APIs)

TezAtlas includes an MCP server that exposes Semantic Scholar, OpenAlex, and CrossRef
as structured tools. To enable it, add to your `claude_desktop_config.json` or `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "tezatlas-academic": {
      "command": "python3",
      "args": ["<absolute-path-to-TezAtlas>/mcp_server/server.py"],
      "env": {
        "S2_API_KEY": "optional-semantic-scholar-key"
      }
    }
  }
}
```

Once connected, the source_hunter agent and find_source.py gain access to richer
semantic search capabilities via the MCP tools.

## Slash Commands

### Core
- `/tezatlas` — start/resume session
- `/import` — import existing academic work (mid-project entry)
- `/status` — read-only status check
- `/review-draft <file>` — 4-layer draft review (args + sources + style + literature alignment)
- `/ai-review` — trigger AI Peer Review at any time (phase gate, section, argument, or saturation)

### Literature Intelligence (9 Academic Analysis Prompts)
- `/intake` — Source map: cluster sources, extract core claims, flag contradictions → SOURCE_MAP.md
- `/contradictions` — Enhanced cross-source contradiction scanner → CONTRADICTIONS.md
- `/citation-chain` — Intellectual lineage: who started → challenged → developed → consensus → CITATION_CHAIN.md
- `/gaps` — Research gap scanner: unanswered questions, coverage gaps → GAPS.md
- `/method-audit` — Methodology audit across sources + user's own method
- `/assumptions` — Untested assumption finder with risk analysis → ASSUMPTIONS.md
- `/knowledge-map` — Field structure: pillars + contentions + boundaries → KNOWLEDGE_MAP.md
- `/so-what` — "So What?" test: 3 essential statements → SO_WHAT.md
- `/synthesize` — Multi-source synthesis by argument → SYNTHESIS.md

### Output & Submission
- `/latex` — Convert Markdown drafts to LaTeX (.tex)
- `/compile-pdf` — Compile LaTeX to PDF via latexmk (with word count)
- `/submission-check` — Pre-submission checklist (word count, citations, structure, blind review)

### Other
- `/devil-advocate` — Challenge claims from 4 angles
- `/citation-check "<claim>" <source.pdf>` — Verify claim vs PDF
- `/generate-citations` — Run BibTeX generator

## Section Infrastructure

`/review-draft` auto-detects section type (Intro/Literature/Method/Results/Discussion/Conclusion)
from filename and content, then applies section-specific checks and tool recommendations.
See `core/literature_intel.py` and `skills/core/section-infrastructure.md`.

## Universal CLI (Non-Claude Usage)

TezAtlas can be used without Claude Code via the universal CLI:
```
python3 tezatlas_cli.py <command> [options]
python3 tezatlas_cli.py intake --project-dir ~/thesis
python3 tezatlas_cli.py import --type thesis --lang tr --field law
python3 tezatlas_cli.py --list
```

All Python scripts and the agents framework (10+ LLM providers via `agents.yaml`)
work independently of Claude. Only the slash command interface (`.claude/commands/`)
is Claude Code-specific.

## Supported Document Types

- Doctoral / Master's Thesis → skills/phases/thesis/
- Journal Article → skills/phases/article/
- Conference Paper → skills/phases/conference/
- Literature Review → skills/phases/lit-review/
- Research Report → skills/phases/report/
- Book Chapter → skills/phases/book-chapter/
- Grant Proposal → skills/phases/grant-proposal/
- Research Proposal / Prospectus → skills/phases/research-proposal/
- Poster → skills/phases/poster/
- Technical Report → skills/phases/technical-report/
