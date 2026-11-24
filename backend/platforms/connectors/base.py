from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BasePlatformConnector(ABC):
    platform_name = "base"

    def __init__(self, username: Optional[str] = None, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        self.username = username
        self.access_token = access_token
        self.refresh_token = refresh_token

    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """Return the public profile payload for the platform."""

    @abstractmethod
    def get_analytics(self) -> Dict[str, Any]:
        """Return platform analytics and insights payloads."""

    @abstractmethod
    def sync(self) -> Dict[str, Any]:
        """Sync profile and analytics payloads from the platform."""
