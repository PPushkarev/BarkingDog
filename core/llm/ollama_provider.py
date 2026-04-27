# core/llm/ollama_provider.py
"""
Ollama provider implementation for BarkingDog.

Wraps the Ollama REST API behind the BaseProvider interface, enabling
fully local LLM inference with no external API keys required.

Ollama must be running and the model pulled before use:
    ollama serve
    ollama pull llama3

json_mode is emulated via format=json in the Ollama API — supported
natively in Ollama ≥ 0.1.24 for models that understand JSON instruction.

Environment variables:
    LLM_MODEL        — model tag to use (default: llama3)
    OLLAMA_BASE_URL  — Ollama server URL (default: http://localhost:11434)
"""

# =============================================================================
# Built-in
# =============================================================================
import json
import os

# =============================================================================
# Third-party
# =============================================================================
import httpx

# =============================================================================
# Local
# =============================================================================
from core.llm.base import BaseProvider

_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_MODEL    = "llama3"

# System-prompt suffix that nudges models without native JSON support
_JSON_SUFFIX = "\n\nRespond with valid JSON only. No markdown, no preamble."


class OllamaProvider(BaseProvider):
    """
    Concrete LLM provider backed by a locally running Ollama server.

    Uses the /api/chat endpoint (multi-turn format) for consistency
    with the OpenAI and Anthropic providers.
    """

    def __init__(self) -> None:
        """
        Reads configuration from environment variables.
        No credentials required — Ollama is local by default.
        """
        self.model    = os.getenv("LLM_MODEL", _DEFAULT_MODEL)
        self.base_url = os.getenv("OLLAMA_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")
        self._chat_url = f"{self.base_url}/api/chat"

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> str:
        """
        Sends a chat completion request to the local Ollama server.

        Args:
            prompt:      User message content.
            system:      System prompt forwarded as a "system" role message.
            temperature: Sampling temperature (0.0 = greedy / most deterministic).
            max_tokens:  Maximum tokens Ollama is allowed to generate.
            json_mode:   Enables Ollama's native format=json + prompt suffix.

        Returns:
            The model's reply as a plain string.

        Raises:
            httpx.HTTPStatusError: If Ollama returns a non-2xx response.
            httpx.ConnectError: If Ollama is not running on OLLAMA_BASE_URL.
        """
        system_text = system + _JSON_SUFFIX if json_mode else system

        messages: list[dict] = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": prompt})

        body: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            # Ollama native JSON mode — forces tokenizer to emit valid JSON
            body["format"] = "json"

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self._chat_url, json=body)
            resp.raise_for_status()

        data = resp.json()
        # Ollama /api/chat returns: {"message": {"role": "assistant", "content": "..."}}
        return data["message"]["content"].strip()

    async def list_models(self) -> list[str]:
        """
        Helper: returns a list of locally available model tags.

        Useful for health checks and CLI tooling.

        Returns:
            List of model name strings (e.g. ['llama3', 'mistral']).
        """
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]