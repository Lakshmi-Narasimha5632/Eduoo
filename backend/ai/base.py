"""Base class for modular AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAIProvider(ABC):
    provider_name = "base"

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a text response from the AI provider."""

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate structured JSON response from the AI provider."""
