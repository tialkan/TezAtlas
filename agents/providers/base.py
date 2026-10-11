"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for all LLM provider implementations."""

    def __init__(self, name: str, default_model: str):
        self.name = name
        self.default_model = default_model

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Send messages and return response text.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
            model: Model override. Uses default_model if None.
            temperature: Sampling temperature.

        Returns:
            The assistant's response text.
        """

    @abstractmethod
    async def health_check(self) -> dict:
        """Send a minimal prompt to verify connectivity.

        Returns:
            {"status": "ok"|"error", "provider": name, "model": ..., "detail": ...}
        """

    def resolve_model(self, model: str | None) -> str:
        return model or self.default_model

    def _kullanim_kaydet(self, model: str, usage) -> None:
        """Yanıttaki token kullanımını bellekte tutar (maliyet görünürlüğü için)."""
        if usage is None:
            return
        girdi = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", 0) or 0
        cikti = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", 0) or 0
        if not hasattr(self, "usage"):
            self.usage = []
        self.usage.append({"model": model, "girdi_token": int(girdi), "cikti_token": int(cikti)})
