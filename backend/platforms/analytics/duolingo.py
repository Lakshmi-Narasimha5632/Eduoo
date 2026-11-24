from __future__ import annotations

from typing import Any, Dict

from .base import PlatformAnalytics


class DuolingoAnalytics(PlatformAnalytics):
    platform_name = "duolingo"

    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "connected": bool(payload.get("connected")),
            "profile": payload.get("profile", {}),
            "analytics": {
                "streak": None,
                "language_count": None,
                "language_progress": None,
                "xp": None,
                "lessons": None,
                "achievements": None,
                "achievement_completion": None,
            },
            "insights": {
                "streak": None,
                "strongest_language": None,
                "weak_language": None,
                "achievement_progress": None,
                "consistency": None,
                "social_engagement": None,
            },
            "recommendations": [],
        }
