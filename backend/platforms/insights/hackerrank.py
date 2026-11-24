"""HackerRank insights generator."""

from __future__ import annotations
from typing import Any, Dict, List
from .base import BasePlatformInsights


class HackerRankInsights(BasePlatformInsights):
    platform_name = "hackerrank"

    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        analytics = analytics_data.get("analytics") or {}
        badges = analytics.get("badges") or 0

        if badges >= 3:
            insights.append({
                "type": "performance",
                "priority": "low",
                "title": "HackerRank Skill Badges Earned",
                "message": f"You've earned {badges} HackerRank badges. Validated skills strengthen your technical resume.",
                "metadata": {"platform": "hackerrank", "badges": badges},
            })
        else:
            insights.append({
                "type": "skill_gap",
                "priority": "medium",
                "title": "Earn Problem Solving Badges",
                "message": "Complete introductory HackerRank problem-solving tracks to earn gold badges.",
                "metadata": {"platform": "hackerrank"},
            })
        return insights
