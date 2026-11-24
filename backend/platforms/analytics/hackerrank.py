from __future__ import annotations

from typing import Any, Dict

from .base import PlatformAnalytics


class HackerRankAnalytics(PlatformAnalytics):
    platform_name = "hackerrank"

    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "connected": bool(payload.get("connected")),
            "profile": payload.get("profile", {}),
            "analytics": {
                "badges": None,
                "certificates": None,
                "skills": None,
                "scores": None,
                "challenges": None,
                "activity": None,
            },
            "insights": {
                "skills_snapshot": None,
                "challenge_consistency": None,
                "assessment_strength": None,
            },
            "recommendations": [],
        }
