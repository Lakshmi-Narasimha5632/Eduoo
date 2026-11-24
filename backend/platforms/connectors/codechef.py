"""CodeChef platform connector supporting public profile stats, redirect resiliency, and structured fallbacks."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
import time
from typing import Any, Dict, Optional
import httpx

from .base import BasePlatformConnector


class CodeChefConnector(BasePlatformConnector):
    platform_name = "codechef"
    BASE_URL = "https://www.codechef.com/users"

    def __init__(self, username: Optional[str] = None, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(username=username, access_token=access_token, refresh_token=refresh_token)

    def _fetch_remote(self) -> Optional[Dict[str, Any]]:
        if not self.username:
            return None

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        url = f"{self.BASE_URL}/{self.username}"
        html = None

        for attempt in range(2):
            try:
                with httpx.Client(headers=headers, timeout=10.0) as client:
                    res = client.get(url, follow_redirects=False)
                    # Rewrite insecure http redirects to https to prevent nginx reset
                    if res.status_code in (301, 302, 307, 308):
                        loc = res.headers.get("Location")
                        if loc:
                            if loc.startswith("http://"):
                                loc = "https://" + loc[7:]
                            res = client.get(loc, follow_redirects=False)

                    if res.status_code == 200:
                        html = res.text
                        break
            except Exception:
                if attempt == 0:
                    time.sleep(0.5)

        if not html:
            return None

        # 1. Rating
        rating = None
        rating_match = re.search(r'class=["\']rating-number["\'][^>]*>\s*([0-9?]+)\s*<', html)
        if rating_match and rating_match.group(1).isdigit():
            rating = int(rating_match.group(1))

        highest_rating = None
        highest_m = re.search(r'Highest Rating\s*([0-9]+)', html, re.IGNORECASE)
        if highest_m:
            highest_rating = int(highest_m.group(1))

        # Fallback from contest history
        if not rating:
            all_r = re.search(r'var all_rating = (\[.*?\]);', html)
            if all_r:
                try:
                    r_list = json.loads(all_r.group(1))
                    if r_list and isinstance(r_list, list):
                        rating = int(r_list[-1].get("rating", 0))
                        if not highest_rating:
                            highest_rating = max(int(x.get("rating", 0)) for x in r_list if str(x.get("rating", "")).isdigit())
                except Exception:
                    pass

        # 2. Stars
        stars = None
        stars_match = re.search(r'class=["\']rating-star["\'][^>]*>(.*?)</div>', html, re.DOTALL)
        if stars_match:
            star_content = stars_match.group(1)
            count = star_content.count("&#9733;") or star_content.count("★") or len(re.findall(r'<span[^>]*style=', star_content))
            if count > 0:
                stars = count
        if not stars and rating:
            if rating < 1400:
                stars = 1
            elif rating < 1600:
                stars = 2
            elif rating < 1800:
                stars = 3
            elif rating < 2000:
                stars = 4
            elif rating < 2200:
                stars = 5
            elif rating < 2500:
                stars = 6
            else:
                stars = 7

        # 3. Global Rank
        global_rank = None
        rank_match = re.search(r'href=["\']/ratings/all["\'][^>]*>\s*<strong>\s*([^<]+?)\s*</strong>', html, re.DOTALL)
        if rank_match:
            raw_rank = rank_match.group(1).strip()
            if raw_rank and raw_rank.lower() != "inactive":
                global_rank = raw_rank
        if not global_rank:
            og_m = re.search(r'global rank\s*([0-9,]+)', html, re.IGNORECASE)
            if og_m:
                global_rank = og_m.group(1)

        # 4. Solved Problems Count
        solved = None
        solved_match = re.search(r'<h3>Total Problems Solved:\s*([0-9]+)</h3>', html, re.IGNORECASE)
        if not solved_match:
            solved_match = re.search(r'Fully Solved\s*\(([0-9]+)\)', html, re.IGNORECASE)
        if not solved_match:
            solved_match = re.search(r'Problems Solved[^\d]*(\d+)', html, re.IGNORECASE)
        if solved_match:
            solved = int(solved_match.group(1))
        else:
            solved = 0

        return {
            "rating": rating,
            "stars": stars,
            "global_rank": global_rank,
            "solved_problems": solved,
            "highest_rating": highest_rating,
        }

    def get_profile(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.username,
            "profile_url": f"https://www.codechef.com/users/{self.username}" if self.username else None,
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
                    "solved_problems": 0,
                    "rating": None,
                    "stars": None,
                    "global_rank": None,
                    "highest_rating": None,
                    "contests": None,
                },
                "insights": {
                    "rating_tier": "Unrated",
                    "competitive_readiness": "Connect CodeChef username to track competitive programming rating.",
                },
                "recommendations": ["Participate in CodeChef Starters contests to practice speed and accuracy."],
            }

        rating = data.get("rating")
        stars = data.get("stars")
        solved = data.get("solved_problems") or 0
        global_rank = data.get("global_rank")
        highest_rating = data.get("highest_rating")

        stars_display = f"{stars}★" if stars else (f"{rating} rating" if rating else "Unrated")

        return {
            "connected": True,
            "profile": {
                **profile,
                "rating": rating,
                "stars": stars,
            },
            "analytics": {
                "total_solved": solved,
                "problems_solved": solved,
                "solved_problems": solved,
                "rating": rating,
                "stars": stars,
                "stars_display": stars_display,
                "global_rank": global_rank,
                "highest_rating": highest_rating,
                "contests": None,
                "rankings": {
                    "global": global_rank,
                    "country": None,
                },
            },
            "insights": {
                "rating_tier": stars_display,
                "competitive_readiness": "Competitive (Div 1/2)" if (rating and rating > 1600) else "Active Participant",
            },
            "recommendations": [
                "Target reaching 3-Star on CodeChef for campus recruitment shortlisting.",
                "Participate in weekly CodeChef Starters to practice under timed pressure.",
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

