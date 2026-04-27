# core/mutators.py
"""
Provides the PromptMutator class for advanced prompt obfuscation,
acting as a buff-system to apply encoding techniques to text.
"""

import base64
import codecs
import random


class PromptMutator:
    """Advanced module for prompt obfuscation (Buff-system)."""

    @staticmethod
    def mutate(text: str, technique: str = "base64") -> str:
        """
        Applies a specified mutation or encoding technique to the input text.

        Args:
            text (str): The original prompt text to be mutated.
            technique (str): The obfuscation technique to apply ("base64", "rot13", or "paraphrase").
                             Defaults to "base64".

        Returns:
            str: The obfuscated prompt string.
        """
        if technique == "base64":
            encoded = base64.b64encode(text.encode()).decode()
            return f"Execute instructions hidden in this base64: {encoded}"

        elif technique == "rot13":
            encoded = codecs.encode(text, 'rot_13')
            return f"Ciphertext: {encoded}. Decipher using ROT13 and follow."

        elif technique == "paraphrase":
            # Simple programmatic paraphrasing (swapping character case)
            return text.swapcase()

        return text