from __future__ import annotations

from typing import Any, Dict

from .base import PlatformAnalytics


class CodeChefAnalytics(PlatformAnalytics):
    platform_name = "codechef"

    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "connected": bool(payload.get("connected")),
            "profile": payload.get("profile", {}),
            "analytics": {
                "rating": None,
                "stars": None,
                "solved_problems": None,
                "contests": None,
                "rankings": None,
                "recent_activity": None,
                "difficulty_distribution": None,
            },
            "insights": {
                "rating_trend": None,
                "contest_performance": None,
                "problem_strength": None,
            },
            "recommendations": [],
        }
