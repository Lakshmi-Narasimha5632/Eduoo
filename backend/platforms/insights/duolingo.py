"""Duolingo insights generator."""

from __future__ import annotations
from typing import Any, Dict, List
from .base import BasePlatformInsights


class DuolingoInsights(BasePlatformInsights):
    platform_name = "duolingo"

    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        analytics = analytics_data.get("analytics") or {}
        streak = analytics.get("streak") or 0

        if streak >= 14:
            insights.append({
                "type": "consistency",
                "priority": "low",
                "title": "Language Learning Habit Formed",
                "message": f"Impressive {streak}-day Duolingo streak! High consistency directly correlates with long-term retention.",
                "metadata": {"platform": "duolingo", "streak": streak},
            })
        elif streak < 3:
            insights.append({
                "type": "consistency",
                "priority": "medium",
                "title": "Build Duolingo Daily Streak",
                "message": "Commit to 10 minutes every morning to form an unbroken learning habit.",
                "metadata": {"platform": "duolingo", "streak": streak},
            })
        return insights
