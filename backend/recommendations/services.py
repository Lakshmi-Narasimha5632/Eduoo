from __future__ import annotations

from typing import Any, Dict, List

from .models import Recommendation


class RecommendationService:
    @staticmethod
    def create_recommendation(user, *, category: str, priority: str, title: str, description: str, action: str, estimated_time: int = 30) -> Recommendation:
        return Recommendation.objects.create(
            user=user,
            category=category,
            priority=priority,
            title=title,
            description=description,
            action=action,
            estimated_time=estimated_time,
        )

    @staticmethod
    def get_user_recommendations(user) -> List[Recommendation]:
        return list(Recommendation.objects.filter(user=user).order_by("-created_at"))

    @staticmethod
    def build_default_recommendations(user, platform_payload: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        recommendations = [
            {
                "category": "study",
                "priority": "high",
                "title": "Practice one medium DSA problem",
                "description": "Reinforce core problem solving patterns with a focused session.",
                "action": "Solve one medium difficulty problem today.",
                "estimated_time": 35,
            },
            {
                "category": "platform",
                "priority": "medium",
                "title": "Improve your project documentation",
                "description": "A clearer README increases project visibility and recruiter confidence.",
                "action": "Update the README of your main project.",
                "estimated_time": 25,
            },
        ]
        if platform_payload and platform_payload.get("platform") == "leetcode":
            recommendations.insert(
                0,
                {
                    "category": "platform",
                    "priority": "high",
                    "title": "Practice more hard problems",
                    "description": "Your data suggests a strong opportunity to improve hard-problem performance.",
                    "action": "Solve 3 hard LeetCode problems this week.",
                    "estimated_time": 60,
                },
            )
        return recommendations
