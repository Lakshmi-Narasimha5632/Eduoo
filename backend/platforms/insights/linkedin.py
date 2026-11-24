"""LinkedIn insights generator."""

from __future__ import annotations
from typing import Any, Dict, List
from .base import BasePlatformInsights


class LinkedInInsights(BasePlatformInsights):
    platform_name = "linkedin"

    def generate(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        profile = analytics_data.get("profile") or {}
        if not profile.get("available"):
            insights.append({
                "type": "career",
                "priority": "medium",
                "title": "Connect LinkedIn Profile",
                "message": "Linking your LinkedIn profile unlocks profile completeness scoring and professional presence tips.",
                "metadata": {"platform": "linkedin"},
            })
        else:
            insights.append({
                "type": "career",
                "priority": "low",
                "title": "Professional Profile Linked",
                "message": "Your professional identity is connected. Keep your headline synced with your target role.",
                "metadata": {"platform": "linkedin"},
            })
        return insights
