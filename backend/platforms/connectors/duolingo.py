"""Duolingo platform connector fetching public user profile and language progress."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx

from .base import BasePlatformConnector


class DuolingoConnector(BasePlatformConnector):
    platform_name = "duolingo"
    BASE_URL = "https://www.duolingo.com/2017-06-30"

    def __init__(self, username: Optional[str] = None, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(username=username, access_token=access_token, refresh_token=refresh_token)

    def _fetch_remote(self) -> Optional[Dict[str, Any]]:
        if not self.username:
            return None
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            with httpx.Client(timeout=6.0, follow_redirects=True) as client:
                res = client.get(f"{self.BASE_URL}/users?username={self.username}", headers=headers)
                if res.status_code == 200:
                    users = res.json().get("users", [])
                    if users and len(users) > 0:
                        return users[0]
        except Exception:
            pass
        return None

    def get_profile(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.username,
            "profile_url": f"https://www.duolingo.com/profile/{self.username}" if self.username else None,
            "available": bool(self.username),
        }

    def get_analytics(self) -> Dict[str, Any]:
        data = self._fetch_remote()
        profile = self.get_profile()

        if not data:
            return {
                "connected": bool(self.username),
                "profile": profile,
                "analytics": {
                    "streak": None,
                    "language_count": None,
                    "language_progress": None,
                    "xp": None,
                    "lessons": None,
                    "achievements": None,
                    "achievement_completion": None,
                },
                "insights": {
                    "streak": None,
                    "strongest_language": None,
                    "weak_language": None,
                    "achievement_progress": None,
                    "consistency": None,
                    "social_engagement": None,
                },
                "recommendations": ["Practice 10-15 minutes daily on Duolingo to build foreign language fluency."],
            }

        streak = data.get("streak", 0)
        total_xp = data.get("totalXp", 0)
        courses = data.get("courses", [])

        lang_progress = {}
        for c in courses:
            title = c.get("title") or c.get("learningLanguage")
            xp = c.get("xp", 0)
            if title:
                lang_progress[title] = {"xp": xp, "crowns": c.get("crowns", 0)}

        strongest_lang = max(lang_progress, key=lambda k: lang_progress[k]["xp"]) if lang_progress else None
        weak_lang = min(lang_progress, key=lambda k: lang_progress[k]["xp"]) if len(lang_progress) > 1 else None

        recommendations = []
        if streak < 7:
            recommendations.append("Reach a 7-day streak on Duolingo to solidify your habit.")
        else:
            recommendations.append(f"Great job maintaining a {streak}-day streak! Keep practicing daily.")

        return {
            "connected": True,
            "profile": {
                **profile,
                "display_name": data.get("name") or self.username,
                "avatar": data.get("picture"),
            },
            "analytics": {
                "streak": streak,
                "language_count": len(courses),
                "language_progress": lang_progress if lang_progress else None,
                "xp": total_xp,
                "lessons": None,  # Field unavailable in public endpoint
                "achievements": None,
                "achievement_completion": None,
            },
            "insights": {
                "streak": f"{streak} days active",
                "strongest_language": strongest_lang,
                "weak_language": weak_lang,
                "achievement_progress": None,
                "consistency": "Strong" if streak >= 7 else "Developing",
                "social_engagement": None,
            },
            "recommendations": recommendations,
        }

    def sync(self) -> Dict[str, Any]:
        analytics_result = self.get_analytics()
        return {
            "platform": self.platform_name,
            "connected": analytics_result["connected"],
            "profile": analytics_result["profile"],
            "analytics": analytics_result["analytics"],
            "insights": analytics_result["insights"],
            "recommendations": analytics_result["recommendations"],
            "last_synced_at": datetime.now(timezone.utc).isoformat(),
        }
