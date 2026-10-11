"""Generic OpenAI-compatible LLM provider.

Covers: OpenAI, Gemini, DeepSeek, Grok, Groq, Together, MiniMax, Ollama,
and any other provider exposing an OpenAI-compatible chat completions endpoint.
"""

from openai import AsyncOpenAI

from agents.providers.base import LLMProvider


class OpenAICompatProvider(LLMProvider):
    """Provider that works with any OpenAI-compatible API."""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        default_model: str,
        timeout: float = 120,
        max_retries: int = 2,
        max_tokens: int = 8192,
    ):
        super().__init__(name=name, default_model=default_model)
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.usage: list[dict] = []
        self.client = AsyncOpenAI(
            base_url=base_url,
            # Yerel sunucular (Ollama) anahtar istemez; SDK boş anahtarı kabul etmediği için yer tutucu.
            api_key=api_key or "yerel-anahtar-gerekmez",
            timeout=timeout,
            max_retries=max_retries,
        )

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        resolved = self.resolve_model(model)
        response = await self.client.chat.completions.create(
            model=resolved,
            messages=messages,
            temperature=temperature,
            max_tokens=self.max_tokens,
        )
        self._kullanim_kaydet(resolved, getattr(response, "usage", None))
        return response.choices[0].message.content or ""

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
