from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class PlatformAnalytics(ABC):
    platform_name = "base"

    @abstractmethod
    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert raw platform data into unified analytics output."""
