"""AI Service manager resolving active provider based on environment configuration."""

from __future__ import annotations

import os
from typing import Any, Dict

from .base import BaseAIProvider
from .fallback import LocalFallbackProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .tokenharbor import TokenHarborProvider


class AIService:
    @staticmethod
    def is_live_ai_available() -> bool:
        if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("TESTING", "").lower() == "true":
            return False
        provider_name = os.getenv("AI_PROVIDER", "").lower().strip()
        has_tokenharbor_key = bool(os.getenv("TOKEN_HARBOR_API_KEY", "").strip())
        has_gemini_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
        has_openai_key = bool(os.getenv("OPENAI_API_KEY", "").strip())

        if provider_name in ("token_harbor", "tokenharbor") and (has_tokenharbor_key or has_gemini_key or has_openai_key):
            return True
        elif provider_name == "gemini" and has_gemini_key:
            return True
        elif provider_name == "openai" and has_openai_key:
            return True

        if has_tokenharbor_key or has_gemini_key or has_openai_key:
            return True
        return False

    @staticmethod
    def get_provider() -> BaseAIProvider:
        if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("TESTING", "").lower() == "true":
            return LocalFallbackProvider()
        provider_name = os.getenv("AI_PROVIDER", "").lower().strip()
        has_tokenharbor_key = bool(os.getenv("TOKEN_HARBOR_API_KEY", "").strip())
        has_gemini_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
        has_openai_key = bool(os.getenv("OPENAI_API_KEY", "").strip())

        if provider_name in ("token_harbor", "tokenharbor"):
            return TokenHarborProvider()
        elif provider_name == "gemini" and has_gemini_key:
            return GeminiProvider()
        elif provider_name == "openai" and has_openai_key:
            return OpenAIProvider()

        # Default precedence when not explicitly overridden
        if has_tokenharbor_key:
            return TokenHarborProvider()
        elif has_gemini_key:
            return GeminiProvider()
        elif has_openai_key:
            return OpenAIProvider()
        return LocalFallbackProvider()

    @staticmethod
    def generate_text(prompt: str, system_prompt: str = "") -> str:
        provider = AIService.get_provider()
        return provider.generate_text(prompt, system_prompt)

    @staticmethod
    def generate_json(prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        provider = AIService.get_provider()
        return provider.generate_json(prompt, system_prompt)
