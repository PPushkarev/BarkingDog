# core/llm/openai_provider.py
"""
OpenAI provider implementation for BarkingDog.

Wraps the AsyncOpenAI client behind the BaseProvider interface.
Reads configuration from environment variables so the caller never
needs to pass credentials explicitly.

Environment variables:
    AI_API_KEY    — OpenAI API key (required)
    LLM_MODEL     — model name (default: gpt-4o-mini)
    LLM_BASE_URL  — base URL override for proxies / Azure (optional)
"""

# =============================================================================
# Built-in
# =============================================================================
import os

# =============================================================================
# Third-party
# =============================================================================
from openai import AsyncOpenAI

# =============================================================================
# Local
# =============================================================================
from core.llm.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    Concrete LLM provider backed by the OpenAI Chat Completions API.

    Supports json_mode via OpenAI's native response_format parameter,
    which guarantees valid JSON output without post-processing.
    """

    def __init__(self) -> None:
        """
        Initialises the AsyncOpenAI client from environment variables.
        Raises no error on missing key — failure surfaces at call time.
        """
        self.model    = os.getenv("LLM_MODEL", "gpt-4o-mini")
        base_url      = os.getenv("LLM_BASE_URL")   # None → uses OpenAI default
        self.client   = AsyncOpenAI(
            api_key=os.getenv("AI_API_KEY"),
            base_url=base_url,
        )

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> str:
        """
        Sends a chat completion request to the OpenAI API.

        Args:
            prompt:      User message content.
            system:      System prompt prepended as a "system" role message.
            temperature: Sampling temperature forwarded to the API.
            max_tokens:  Token cap for the completion.
            json_mode:   Enables OpenAI's response_format=json_object mode.

        Returns:
            The model's reply as a plain string.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = dict(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI returned None content")
        return content.strip()