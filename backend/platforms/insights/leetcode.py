"""LeetCode insights generator."""

from __future__ import annotations
from typing import Any, Dict, List
from .base import BasePlatformInsights


class LeetCodeInsights(BasePlatformInsights):
    platform_name = "leetcode"

    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        analytics = analytics_data.get("analytics") or {}
        hard = analytics.get("hard_solved") or 0
        medium = analytics.get("medium_solved") or 0
        total = analytics.get("total_solved") or 0

        if hard < 10:
            insights.append({
                "type": "difficulty",
                "priority": "high",
                "title": "Increase Hard Problem Practice",
                "message": f"You have solved {hard} Hard problems. Aim for at least 15 to excel in senior interview rounds.",
                "metadata": {"platform": "leetcode", "category": "difficulty"},
            })
        if medium >= 30:
            insights.append({
                "type": "performance",
                "priority": "medium",
                "title": "Solid Medium Problem Foundation",
                "message": f"You've solved {medium} Medium problems. Your foundational algorithms grasp is strong.",
                "metadata": {"platform": "leetcode", "category": "performance"},
            })
        if total > 0 and (analytics.get("activity_last_7_days") or 0) == 0:
            insights.append({
                "type": "consistency",
                "priority": "medium",
                "title": "Resume Weekly LeetCode Practice",
                "message": "No problems solved in the last 7 days. Consistency is key for retention.",
                "metadata": {"platform": "leetcode", "category": "consistency"},
            })
        return insights
