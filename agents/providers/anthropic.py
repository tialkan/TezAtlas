"""Anthropic-specific LLM provider.

Uses the Anthropic SDK (different message format from OpenAI).
Only needed when users want to call Claude API directly outside Claude Code.
"""

from anthropic import AsyncAnthropic

from agents.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude models."""

    def __init__(
        self,
        name: str,
        api_key: str,
        default_model: str,
        timeout: float = 120,
        max_retries: int = 2,
        max_tokens: int = 8192,
    ):
        super().__init__(name=name, default_model=default_model)
        self.max_tokens = max_tokens
        self.usage: list[dict] = []
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout, max_retries=max_retries)

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        resolved = self.resolve_model(model)

        # Separate system message from conversation messages.
        # Birden fazla sistem mesajı varsa hepsi korunur (eskiden yalnız sonuncusu kalıyordu).
        system_parts: list[str] = []
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                chat_messages.append(msg)
        system_text = "\n\n".join(system_parts) or None

        kwargs: dict = {
            "model": resolved,
            "max_tokens": self.max_tokens,
            "messages": chat_messages,
            "temperature": temperature,
        }
        if system_text:
            kwargs["system"] = system_text

        response = await self.client.messages.create(**kwargs)
        self._kullanim_kaydet(resolved, getattr(response, "usage", None))
        return "".join(getattr(b, "text", "") for b in response.content)

    async def health_check(self) -> dict:
        model = self.default_model
        try:
            result = await self.chat(
                messages=[{"role": "user", "content": "Reply with OK"}],
                model=model,
                temperature=0,
            )
            return {
                "status": "ok",
                "provider": self.name,
                "model": model,
                "detail": result[:100],
            }
        except Exception as exc:
            return {
                "status": "error",
                "provider": self.name,
                "model": model,
                "detail": str(exc)[:200],
            }
