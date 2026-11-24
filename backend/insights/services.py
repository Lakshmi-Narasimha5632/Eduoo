from __future__ import annotations

from typing import Any, Dict, List

from .models import Insight


class InsightService:
    @staticmethod
    def create_insight(user, *, insight_type: str, priority: str, title: str, message: str, metadata: Dict[str, Any] | None = None) -> Insight:
        return Insight.objects.create(
            user=user,
            type=insight_type,
            priority=priority,
            title=title,
            message=message,
            metadata=metadata or {},
        )

    @staticmethod
    def get_user_insights(user) -> List[Insight]:
        return list(Insight.objects.filter(user=user).order_by("-created_at"))

    @staticmethod
    def build_platform_insights(user, platform_name: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        if payload.get("connected") is False:
            return insights

        if platform_name == "leetcode":
            insights.append({
                "type": "difficulty",
                "priority": "medium",
                "title": "LeetCode difficulty balance",
                "message": "Focus on medium and hard problems to improve problem solving depth.",
                "metadata": {"platform": platform_name},
            })

        if platform_name == "github":
            insights.append({
                "type": "activity",
                "priority": "medium",
                "title": "GitHub activity",
                "message": "Keep recent project activity visible and document your work clearly.",
                "metadata": {"platform": platform_name},
            })

        if platform_name == "duolingo":
            insights.append({
                "type": "consistency",
                "priority": "low",
                "title": "Language practice consistency",
                "message": "Daily short language sessions improve retention more than occasional long sessions.",
                "metadata": {"platform": platform_name},
            })

        return insights
