"""HackerRank platform connector supporting public profile scraping and graceful data fallback."""

from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import httpx

from .base import BasePlatformConnector


class HackerRankConnector(BasePlatformConnector):
    platform_name = "hackerrank"
    BASE_API_URL = "https://www.hackerrank.com/rest/hackers"

    def __init__(self, username: Optional[str] = None, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(username=username, access_token=access_token, refresh_token=refresh_token)

    def _fetch_remote(self) -> Optional[Dict[str, Any]]:
        if not self.username:
            return None

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

        user_model = None
        badges = []
        scores = []

        # Retry with backoff for resilience against transient DNS/network drops
        for attempt in range(2):
            try:
                with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                    # 1. Main HackerRank User Profile
                    res_user = client.get(f"{self.BASE_API_URL}/{self.username}", headers=headers)
                    if res_user.status_code == 200:
                        user_model = res_user.json().get("model")

                    # 2. Badges (contains stars, points, solved count per track)
                    res_badges = client.get(f"{self.BASE_API_URL}/{self.username}/badges", headers=headers)
                    if res_badges.status_code == 200:
                        badges = res_badges.json().get("models") or []

                    # 3. Track Scores & Practice Ranks
                    res_scores = client.get(f"{self.BASE_API_URL}/{self.username}/scores_elo", headers=headers)
                    if res_scores.status_code == 200:
                        scores = res_scores.json() if isinstance(res_scores.json(), list) else []

                    if user_model is not None:
                        break
            except Exception:
                if attempt == 0:
                    time.sleep(0.5)

        if not user_model and not badges:
            return None

        total_solved = sum(int(b.get("solved", 0)) for b in badges)
        total_stars = sum(int(b.get("stars", 0)) for b in badges)

        formatted_badges = [
            {
                "badge_name": b.get("badge_name"),
                "stars": b.get("stars", 0),
                "solved": b.get("solved", 0),
                "current_points": b.get("current_points", 0),
            }
            for b in badges
        ]

        active_tracks = [
            s.get("name")
            for s in scores
            if isinstance(s, dict) and (s.get("practice", {}).get("score", 0) > 0 or s.get("name"))
        ][:5]

        return {
            "model": user_model or {},
            "badges": formatted_badges,
            "total_solved": total_solved,
            "total_stars": total_stars,
            "scores": scores,
            "active_tracks": active_tracks,
        }

    def get_profile(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.username,
            "profile_url": f"https://www.hackerrank.com/profile/{self.username}" if self.username else None,
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
                    "total_solved": 0,
                    "problems_solved": 0,
                    "badges": 0,
                    "stars": 0,
                    "certificates": 0,
                    "skills": [],
                    "scores": [],
                    "challenges": 0,
                },
                "insights": {
                    "status": "Public profile linked" if self.username else "Not connected",
                    "domain_strength": None,
                },
                "recommendations": ["Earn problem-solving and language badges on HackerRank."],
            }

        user_info = data.get("model", {})
        badges = data.get("badges", [])
        total_solved = data.get("total_solved", 0)
        total_stars = data.get("total_stars", 0)
        active_tracks = data.get("active_tracks", [])

        # Display name & avatar
        display_name = user_info.get("name") or self.username
        avatar = user_info.get("avatar")
        country = user_info.get("country")
        languages = user_info.get("languages")

        top_badge_names = [b["badge_name"] for b in badges if b.get("badge_name")][:3]

        return {
            "connected": True,
            "profile": {
                **profile,
                "display_name": display_name,
                "avatar": avatar,
                "country": country,
                "languages": languages,
            },
            "analytics": {
                "total_solved": total_solved,
                "problems_solved": total_solved,
                "challenges": total_solved,
                "badges": len(badges),
                "stars": total_stars,
                "badges_list": badges,
                "top_badges": top_badge_names,
                "skills": active_tracks,
                "certificates": len(user_info.get("certificates", [])),
                "country": country,
            },
            "insights": {
                "status": f"{len(badges)} badges earned • {total_solved} solved",
                "domain_strength": top_badge_names[0] if top_badge_names else "Problem Solving",
            },
            "recommendations": [
                f"Continue progress on HackerRank {top_badge_names[0]} badge track." if top_badge_names else "Earn 5-star Problem Solving certification on HackerRank.",
                "Compete in HackerRank Week of Code contests to build competition rating.",
            ],
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

