from __future__ import annotations

from typing import Any, Dict

from .base import PlatformAnalytics


class LeetCodeAnalytics(PlatformAnalytics):
    platform_name = "leetcode"

    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        analytics = {
            "connected": bool(payload.get("connected")),
            "profile": payload.get("profile", {}),
            "analytics": {
                "total_solved": None,
                "easy_solved": None,
                "medium_solved": None,
                "hard_solved": None,
                "ranking": None,
                "activity_today": None,
                "activity_last_7_days": None,
                "activity_last_30_days": None,
                "difficulty_distribution": None,
                "topic_distribution": None,
                "growth": None,
            },
            "insights": {
                "progress": None,
                "difficulty_weakness": None,
                "strongest_topic": None,
                "topic_gaps": [],
                "consistency": None,
                "recommendations": [],
            },
            "recommendations": [],
        }
        return analytics
