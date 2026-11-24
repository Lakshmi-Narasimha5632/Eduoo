from __future__ import annotations

from typing import Any, Dict

from .base import PlatformAnalytics


class LinkedInAnalytics(PlatformAnalytics):
    platform_name = "linkedin"

    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "connected": bool(payload.get("connected")),
            "profile": payload.get("profile", {}),
            "analytics": {
                "connections": None,
                "headline": None,
                "experience_summary": None,
                "profile_visibility": None,
            },
            "insights": {
                "profile_strength": None,
                "experience_signal": None,
                "network_strength": None,
                "headline_quality": None,
            },
            "recommendations": [],
        }
