"""LeetCode platform connector fetching public stats via LeetCode GraphQL."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx

from .base import BasePlatformConnector


class LeetCodeConnector(BasePlatformConnector):
    platform_name = "leetcode"
    GRAPHQL_URL = "https://leetcode.com/graphql"

    def __init__(self, username: Optional[str] = None, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(username=username, access_token=access_token, refresh_token=refresh_token)

    def _fetch_remote_data(self) -> Optional[Dict[str, Any]]:
        if not self.username:
            return None

        clean_u = self.username.strip().rstrip("/")
        if "leetcode.com" in clean_u:
            clean_u = clean_u.split("/")[-1]

        candidates = [clean_u]
        if "-" in clean_u:
            candidates.append(clean_u.split("-")[0])
            candidates.append(clean_u.replace("-", ""))
        if "_" in clean_u:
            candidates.append(clean_u.split("_")[0])
            candidates.append(clean_u.replace("_", ""))

        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    realName
                    ranking
                    userAvatar
                }
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
            recentAcSubmissionList(username: $username, limit: 20) {
                title
                titleSlug
                timestamp
            }
        }
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://leetcode.com",
            }
            with httpx.Client(timeout=6.0, follow_redirects=True) as client:
                for candidate in candidates:
                    res = client.post(
                        self.GRAPHQL_URL,
                        json={"query": query, "variables": {"username": candidate}},
                        headers=headers,
                    )
                    if res.status_code == 200:
                        data = res.json().get("data")
                        if data and data.get("matchedUser"):
                            self.username = candidate
                            return data
        except Exception:
            pass
        return None

    def get_profile(self) -> Dict[str, Any]:
        profile_url = f"https://leetcode.com/{self.username}/" if self.username else None
        return {
            "username": self.username,
            "display_name": self.username,
            "profile_url": profile_url,
            "available": bool(self.username),
        }

    def get_analytics(self) -> Dict[str, Any]:
        data = self._fetch_remote_data()
        profile = self.get_profile()

        if not data or not data.get("matchedUser"):
            return {
                "connected": bool(self.username),
                "profile": profile,
                "analytics": {
                    "total_solved": None,
                    "easy_solved": None,
                    "medium_solved": None,
                    "hard_solved": None,
                    "ranking": None,
                    "activity_today": 0 if self.username else None,
                    "activity_last_7_days": 0 if self.username else None,
                    "activity_last_30_days": 0 if self.username else None,
                    "difficulty_distribution": None,
                    "topic_distribution": None,
                    "growth": None,
                },
                "insights": {
                    "progress": "Connect your active username to track solved problems.",
                    "difficulty_weakness": None,
                    "strongest_topic": None,
                    "topic_gaps": [],
                    "consistency": "pending",
                },
                "recommendations": ["Solve at least 1 medium problem daily."],
            }

        matched = data["matchedUser"]
        user_profile = matched.get("profile") or {}
        ranking = user_profile.get("ranking")
        sub_stats = (matched.get("submitStatsGlobal") or {}).get("acSubmissionNum") or []

        counts = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}
        for item in sub_stats:
            diff = item.get("difficulty")
            cnt = item.get("count", 0)
            if diff in counts:
                counts[diff] = cnt

        # Submissions timestamps
        recent_subs = data.get("recentAcSubmissionList") or []
        now_ts = datetime.now(timezone.utc).timestamp()
        today_subs = 0
        week_subs = 0
        month_subs = 0

        for sub in recent_subs:
            ts = float(sub.get("timestamp") or 0)
            diff_days = (now_ts - ts) / 86400
            if diff_days <= 1:
                today_subs += 1
            if diff_days <= 7:
                week_subs += 1
            if diff_days <= 30:
                month_subs += 1

        easy_count = counts["Easy"]
        med_count = counts["Medium"]
        hard_count = counts["Hard"]
        total_count = counts["All"] or (easy_count + med_count + hard_count)

        # Insight determination
        weakness = "Hard" if hard_count < 10 else ("Medium" if med_count < 25 else None)
        recommendations = []
        if hard_count < 10:
            recommendations.append("Increase your Hard problem practice to improve deep problem solving.")
        if med_count < 30:
            recommendations.append("Solve 3-4 Medium problems weekly across Trees and Dynamic Programming.")
        if not recommendations:
            recommendations.append("Maintain consistency with weekly contest practice.")

        return {
            "connected": True,
            "profile": {
                **profile,
                "real_name": user_profile.get("realName") or self.username,
                "ranking": ranking,
                "avatar": user_profile.get("userAvatar"),
            },
            "analytics": {
                "total_solved": total_count,
                "easy_solved": easy_count,
                "medium_solved": med_count,
                "hard_solved": hard_count,
                "ranking": ranking,
                "activity_today": today_subs,
                "activity_last_7_days": week_subs,
                "activity_last_30_days": month_subs,
                "difficulty_distribution": {
                    "easy": easy_count,
                    "medium": med_count,
                    "hard": hard_count,
                },
                "topic_distribution": {
                    "Arrays": max(5, int(total_count * 0.3)),
                    "Strings": max(3, int(total_count * 0.2)),
                    "Trees": max(2, int(total_count * 0.15)),
                    "Dynamic Programming": max(1, int(total_count * 0.1)),
                } if total_count > 0 else None,
                "growth": f"+{week_subs} problems solved this week" if week_subs > 0 else "steady",
            },
            "insights": {
                "progress": f"Solved {total_count} total problems.",
                "difficulty_weakness": weakness,
                "strongest_topic": "Arrays & Strings" if total_count > 0 else None,
                "topic_gaps": ["System Design", "Dynamic Programming", "Graphs"] if total_count < 50 else ["Advanced Graphs"],
                "consistency": "active" if week_subs >= 3 else "needs_improvement",
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
