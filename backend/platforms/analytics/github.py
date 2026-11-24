from __future__ import annotations

from typing import Any, Dict

from .base import PlatformAnalytics


class GitHubAnalytics(PlatformAnalytics):
    platform_name = "github"

    def build(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "connected": bool(payload.get("connected")),
            "profile": payload.get("profile", {}),
            "analytics": {
                "total_repositories": None,
                "stars": None,
                "forks": None,
                "archived_repositories": None,
                "forked_repositories": None,
                "language_distribution": None,
                "activity_last_7_days": None,
                "activity_last_30_days": None,
                "event_types": None,
            },
            "insights": {
                "strongest_language": None,
                "project_portfolio_strength": None,
                "activity_consistency": None,
                "repository_quality": None,
                "documentation_recommendations": [],
                "visibility_recommendations": [],
            },
            "recommendations": [],
        }
