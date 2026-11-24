"""CodeChef insights generator."""

from __future__ import annotations
from typing import Any, Dict, List
from .base import BasePlatformInsights


class CodeChefInsights(BasePlatformInsights):
    platform_name = "codechef"

    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        analytics = analytics_data.get("analytics") or {}
        rating = analytics.get("rating")
        stars = analytics.get("stars")

        if rating and rating >= 1600:
            insights.append({
                "type": "performance",
                "priority": "low",
                "title": f"Strong CodeChef Rating ({rating})",
                "message": f"You hold a {stars or ''}★ rating ({rating}). You have strong competitive problem solving speed.",
                "metadata": {"platform": "codechef", "rating": rating},
            })
        elif rating and rating < 1400:
            insights.append({
                "type": "difficulty",
                "priority": "medium",
                "title": "Advance on CodeChef Div 3/4",
                "message": "Focus on solving problems A, B, and C quickly in rated contests to push rating above 1500.",
                "metadata": {"platform": "codechef", "rating": rating},
            })
        return insights
