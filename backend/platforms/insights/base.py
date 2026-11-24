"""Base class for platform-specific insights generation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BasePlatformInsights(ABC):
    platform_name = "base"

    @abstractmethod
    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate structured insights from platform analytics data."""
