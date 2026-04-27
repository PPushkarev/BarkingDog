# core/llm/base.py
"""
Abstract base class for all LLM provider implementations.

Every provider must implement a single async `complete()` method.
This interface is the only contract that the rest of BarkingDog
depends on — switching providers requires no changes outside this package.
"""

# =============================================================================
# Built-in
# =============================================================================
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Minimal async interface for LLM completion providers.

    Subclasses must implement complete() and may expose additional
    provider-specific configuration in their __init__.
    """

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> str:
        """
        Sends a completion request to the underlying LLM provider.

        Args:
            prompt:      User-turn content to send.
            system:      System prompt / instruction prefix.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens:  Maximum tokens in the completion response.
            json_mode:   If True, instruct the model to return valid JSON only.

        Returns:
            The model's response as a plain string.
        """
        ...