# core/llm/factory.py
"""
Provider factory for BarkingDog's LLM layer.

Single entry point for all LLM access. Reads LLM_PROVIDER from the
environment and returns the matching BaseProvider implementation.

Environment variables:
    LLM_PROVIDER — one of: openai | anthropic | ollama  (default: openai)

Usage:
    from core.llm.factory import get_provider

    llm = get_provider()
    text = await llm.complete(prompt="...", system="...", json_mode=True)
"""

# =============================================================================
# Built-in
# =============================================================================
import os
from functools import lru_cache

# =============================================================================
# Local
# =============================================================================
from core.llm.base import BaseProvider

# Supported providers mapped to their import paths.
# Add new entries here when a provider module is created.
_PROVIDER_MAP: dict[str, tuple[str, str]] = {
    "openai":    ("core.llm.openai_provider",    "OpenAIProvider"),
    "anthropic": ("core.llm.anthropic_provider", "AnthropicProvider"),
    "ollama":    ("core.llm.ollama_provider",    "OllamaProvider"),
}


def get_provider(provider_name: str | None = None) -> BaseProvider:
    """
    Instantiates and returns the configured LLM provider.

    Provider is resolved in priority order:
      1. Explicit argument (useful for tests / one-off overrides)
      2. LLM_PROVIDER environment variable
      3. Falls back to "openai"

    Args:
        provider_name: Optional override. Pass None to read from env.

    Returns:
        A concrete BaseProvider instance ready for async use.

    Raises:
        ValueError: If the resolved provider name is not in _PROVIDER_MAP.
        ImportError: If the provider module or class cannot be imported.
    """
    name = (provider_name or os.getenv("LLM_PROVIDER", "openai")).lower().strip()

    if name not in _PROVIDER_MAP:
        supported = ", ".join(sorted(_PROVIDER_MAP))
        raise ValueError(
            f"Unknown LLM_PROVIDER '{name}'. Supported: {supported}"
        )

    module_path, class_name = _PROVIDER_MAP[name]

    # Lazy import keeps startup cost zero for unused providers
    import importlib
    module = importlib.import_module(module_path)
    provider_cls = getattr(module, class_name)

    return provider_cls()


@lru_cache(maxsize=1)
def get_cached_provider() -> BaseProvider:
    """
    Singleton-style provider for use inside long-running processes.

    Reads LLM_PROVIDER once at first call and caches the instance.
    Use get_provider() directly in tests where isolation matters.

    Returns:
        A shared BaseProvider instance (same object on every call).
    """
    return get_provider()