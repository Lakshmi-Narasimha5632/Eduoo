"""GitHub insights generator."""

from __future__ import annotations
from typing import Any, Dict, List
from .base import BasePlatformInsights


class GitHubInsights(BasePlatformInsights):
    platform_name = "github"

    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        analytics = analytics_data.get("analytics") or {}
        repos = analytics.get("total_repositories") or 0
        stars = analytics.get("stars") or 0
        act_7 = analytics.get("activity_last_7_days") or 0

        if repos > 0 and stars == 0:
            insights.append({
                "type": "activity",
                "priority": "medium",
                "title": "Boost Project Visibility",
                "message": "Add visual demos, badges, and detailed README files to your repositories to gain recruiter stars and interest.",
                "metadata": {"platform": "github", "category": "activity"},
            })
        if act_7 >= 5:
            insights.append({
                "type": "consistency",
                "priority": "low",
                "title": "Active GitHub Momentum",
                "message": f"{act_7} events recorded in the last 7 days. Excellent engineering consistency!",
                "metadata": {"platform": "github", "category": "consistency"},
            })
        elif act_7 == 0 and repos > 0:
            insights.append({
                "type": "consistency",
                "priority": "medium",
                "title": "Keep GitHub Contributions Active",
                "message": "No commits or PRs in the last 7 days. Push code regularly to demonstrate continuous learning.",
                "metadata": {"platform": "github", "category": "consistency"},
            })
        return insights
