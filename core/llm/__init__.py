# core/llm/__init__.py
"""
Unified LLM provider layer for BarkingDog.

Public API — everything a caller needs:

    from core.llm import get_provider, get_cached_provider, BaseProvider

    llm = get_provider()                     # fresh instance, reads LLM_PROVIDER
    llm = get_cached_provider()              # shared singleton for long-running processes

    text = await llm.complete(
        prompt="...",
        system="...",
        temperature=0.0,
        max_tokens=1000,
        json_mode=True,
    )

Supported providers (set via LLM_PROVIDER env var):
    openai      — OpenAI Chat Completions API  (default)
    anthropic   — Anthropic Messages API
    ollama      — Local Ollama server (no API key required)
"""

from core.llm.base import BaseProvider
from core.llm.factory import get_cached_provider, get_provider

__all__ = [
    "BaseProvider",
    "get_provider",
    "get_cached_provider",
]