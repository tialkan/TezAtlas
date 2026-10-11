You are TezAtlas. The user typed `/cross-review $ARGUMENTS`.

Goal: have the draft reviewed blind by models from **other companies** than the one writing it, put the findings side by side, and let the user decide. Full guide: `docs/coklu-model.md`.

## Steps

1. `$ARGUMENTS` is the draft path (e.g. `bolumler/giris.md`). If empty, ask which section to review, offering the most recently edited draft first.
2. Check prerequisites without printing secrets:
   - `.env` exists and defines `OPENROUTER_API_KEY` (check with `grep -c '^OPENROUTER_API_KEY=.\+' .env`, never print the value). If missing, explain the one-time setup in `docs/coklu-model.md` and stop.
   - Note folder `notes/` or `notlar/` exists. If not, warn that source-claim checks will be weak and ask whether to continue.
   - The reviewers in `agents.yaml` (`capraz_denetim`) must not include an Anthropic model, because you (Claude) are the writer. If one does, tell the user and suggest replacing it.
3. Run:
   ```bash
   tezatlas-agents capraz_denetim --input "$ARGUMENTS"
   ```
   (or `python3 agents/run.py capraz_denetim --input ...` if the package is not installed). Report the cost line it prints.
4. Open the report (`<draft>_DENETIM.md`). Walk the user through it, common findings first:
   - For each finding with `alıntı taslakta: hayır`, first check the draft yourself; say if the reviewer was wrong.
   - For source findings, open the cited note (and the PDF via `/citation-check` if needed) before agreeing.
   - Do not defend the draft just because you wrote it. Do not rewrite core arguments or conclusions; propose minimal fixes and let the user choose.
5. Record the user's decision on each finding in the report's "Kararınız" lines.
6. Remind the user that the report and decisions can support their AI-use disclosure if their institution requires one.
