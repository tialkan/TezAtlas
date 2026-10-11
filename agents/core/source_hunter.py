"""Source Hunter Agent — discovers and recommends academic sources."""

from __future__ import annotations

import json
from pathlib import Path

from agents.core.kaynak_dogrulama import onerileri_dogrula
from agents.providers.base import LLMProvider

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "source_hunter.md"


class SourceHunterAgent:
    """Searches and evaluates academic sources for a research question."""

    def __init__(self, provider: LLMProvider, model: str | None = None, verify: bool = True):
        self.provider = provider
        self.model = model
        # Model önerileri Crossref ile denetlenir; testlerde kapatılabilir.
        self.verify = verify
        self.system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")

    async def run(
        self,
        research_question: str,
        field: str,
        existing_sources: list[str] | None = None,
        language_preference: str = "both",
    ) -> dict:
        """Run the source discovery pipeline.

        Returns parsed JSON with recommendations, or raw text on parse failure.
        """
        user_payload = json.dumps({
            "research_question": research_question,
            "field": field,
            "existing_sources": existing_sources or [],
            "language_preference": language_preference,
        }, ensure_ascii=False)

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_payload},
        ]

        raw = await self.provider.chat(messages, model=self.model)
        parsed = _parse_json(raw)
        if self.verify and not parsed.get("_parse_error"):
            parsed = await onerileri_dogrula(parsed)
        return parsed


def _parse_json(text: str) -> dict:
    """Best-effort JSON parse, stripping markdown fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove ```json ... ``` wrapper
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_response": text, "_parse_error": True}
