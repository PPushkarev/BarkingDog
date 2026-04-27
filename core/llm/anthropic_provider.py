# core/llm/anthropic_provider.py
"""
Anthropic provider implementation for BarkingDog.

Wraps the Anthropic AsyncAnthropic client behind the BaseProvider interface.
json_mode is emulated via a system-prompt suffix because Anthropic does not
expose a native response_format parameter.

Environment variables:
    AI_API_KEY   — Anthropic API key (required, prefix: sk-ant-...)
    LLM_MODEL    — model name (default: claude-haiku-4-5-20251001)
"""

# =============================================================================
# Built-in
# =============================================================================
import os

# =============================================================================
# Third-party
# =============================================================================
import anthropic

# =============================================================================
# Local
# =============================================================================
from core.llm.base import BaseProvider

# Suffix appended to the system prompt when json_mode=True.
# Mirrors the instruction used by OpenAI's response_format under the hood.
_JSON_SUFFIX = "\n\nRespond with valid JSON only. No markdown, no explanation."


class AnthropicProvider(BaseProvider):
    """
    Concrete LLM provider backed by the Anthropic Messages API.

    Uses AsyncAnthropic for non-blocking calls compatible with the
    rest of BarkingDog's async pipeline.
    """

    def __init__(self) -> None:
        """
        Initialises the AsyncAnthropic client from environment variables.
        """
        self.model = os.getenv("LLM_MODEL", "claude-haiku-4-5")
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv("AI_API_KEY"))

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> str:
        """
        Sends a messages request to the Anthropic API.

        json_mode appends an instruction suffix to the system prompt because
        Anthropic does not support response_format natively.

        Args:
            prompt:      User message content.
            system:      System prompt. If empty, no system block is sent.
            temperature: Sampling temperature forwarded to the API.
            max_tokens:  Token cap for the completion.
            json_mode:   Appends a JSON-only instruction to the system prompt.

        Returns:
            The model's reply as a plain string.
        """
        # Emulate json_mode via prompt engineering
        system_text = system + _JSON_SUFFIX if json_mode else system

        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if system_text:
            kwargs["system"] = system_text

        response = await self.client.messages.create(**kwargs)
        if not response.content:
            raise ValueError("Anthropic returned empty content block")
        text = response.content[0].text
        if text is None:
            raise ValueError("Anthropic returned None text")
        return text.strip()