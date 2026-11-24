"""Platform service orchestrating connectors, syncs, insights, and unified analytics."""

from __future__ import annotations

from django.utils import timezone
from typing import Any, Dict, Optional

from .connectors.base import BasePlatformConnector
from .connectors.codechef import CodeChefConnector
from .connectors.duolingo import DuolingoConnector
from .connectors.github import GitHubConnector
from .connectors.hackerrank import HackerRankConnector
from .connectors.leetcode import LeetCodeConnector
from .connectors.linkedin import LinkedInConnector
from .insights import get_platform_insights_generator
from .models import ConnectedPlatform, LeetCodeCatalogProblem, LeetCodeUserSolvedProblem

CONNECTOR_MAP = {
    "leetcode": LeetCodeConnector,
    "github": GitHubConnector,
    "duolingo": DuolingoConnector,
    "linkedin": LinkedInConnector,
    "hackerrank": HackerRankConnector,
    "codechef": CodeChefConnector,
}


class PlatformService:
    @staticmethod
    def get_connector(
        platform: str,
        username: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> BasePlatformConnector:
        connector_class = CONNECTOR_MAP.get(platform)
        if connector_class is None:
            raise ValueError(f"Unsupported platform: {platform}")
        return connector_class(username=username, access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def sync_platform(
        platform: str,
        username: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        user=None,
    ) -> Dict[str, Any]:
        connector = PlatformService.get_connector(platform, username, access_token, refresh_token)
        payload = connector.sync()

        # Enrich insights with domain generator
        generator = get_platform_insights_generator(platform)
        if generator:
            generated_insights = generator.generate(payload)
            if generated_insights:
                existing_insights = payload.get("insights")
                if isinstance(existing_insights, dict):
                    existing_insights["items"] = generated_insights
                elif isinstance(existing_insights, list):
                    existing_insights.extend(generated_insights)
                else:
                    payload["insights"] = generated_insights

        # Persist to database if user is supplied
        if user and user.is_authenticated:
            # Sync LeetCode problems if applicable
            if platform == "leetcode":
                PlatformService._sync_leetcode_problems(user, payload)

            # Save platform insights
            PlatformService._persist_insights_and_recs(user, platform, payload)

            # Auto-save resolved username and cached analytics
            rec = ConnectedPlatform.objects.filter(user=user, platform=platform).first()
            if rec:
                resolved_user = connector.username or username
                rec.username = resolved_user
                rec.cached_analytics = payload.get("analytics") or payload
                rec.last_synced_at = timezone.now()
                rec.sync_status = "success"
                rec.sync_error = None
                rec.connected = True
                rec.save(update_fields=["username", "cached_analytics", "last_synced_at", "sync_status", "sync_error", "connected", "updated_at"])

                # Trigger real-time platform sync notification & email
                try:
                    from notifications.services import NotificationService
                    plat_display = platform.replace("_", " ").title()
                    solved = (
                        payload.get("total_solved")
                        or payload.get("analytics", {}).get("total_solved")
                        or payload.get("problems_solved")
                        or "N/A"
                    )
                    rating = payload.get("rating") or payload.get("analytics", {}).get("rating") or "N/A"
                    metrics = {"Platform": plat_display, "Problems Solved": str(solved)}
                    if rating != "N/A":
                        metrics["Rating"] = str(rating)

                    NotificationService.create_notification(
                        user=user,
                        title=f"{plat_display} Telemetry Synchronized ⚡",
                        message=f"Real-time telemetry for {plat_display} successfully refreshed. Solved problems: {solved}.",
                        category="platform_sync",
                        send_email=True,
                        action_url="http://localhost:5173/platforms",
                        action_label="View Connected Platforms",
                        extra_metrics=metrics,
                    )
                except Exception:
                    pass

        return payload

    @staticmethod
    def _sync_leetcode_problems(user, payload: Dict[str, Any]):
        analytics = payload.get("analytics") or {}
        diff_dist = analytics.get("difficulty_distribution") or {}
        # Populate catalog seed if empty
        if not LeetCodeCatalogProblem.objects.exists():
            seed_problems = [
                {"title": "Two Sum", "slug": "two-sum", "difficulty": "Easy", "topics": ["Array", "Hash Table"], "problem_url": "https://leetcode.com/problems/two-sum/", "external_id": "1"},
                {"title": "Add Two Numbers", "slug": "add-two-numbers", "difficulty": "Medium", "topics": ["Linked List", "Math"], "problem_url": "https://leetcode.com/problems/add-two-numbers/", "external_id": "2"},
                {"title": "Longest Substring Without Repeating Characters", "slug": "longest-substring-without-repeating-characters", "difficulty": "Medium", "topics": ["Hash Table", "Sliding Window"], "problem_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "external_id": "3"},
                {"title": "Median of Two Sorted Arrays", "slug": "median-of-two-sorted-arrays", "difficulty": "Hard", "topics": ["Array", "Binary Search", "Divide and Conquer"], "problem_url": "https://leetcode.com/problems/median-of-two-sorted-arrays/", "external_id": "4"},
                {"title": "Valid Parentheses", "slug": "valid-parentheses", "difficulty": "Easy", "topics": ["String", "Stack"], "problem_url": "https://leetcode.com/problems/valid-parentheses/", "external_id": "20"},
                {"title": "Trapping Rain Water", "slug": "trapping-rain-water", "difficulty": "Hard", "topics": ["Array", "Two Pointers", "Dynamic Programming"], "problem_url": "https://leetcode.com/problems/trapping-rain-water/", "external_id": "42"},
            ]
            for sp in seed_problems:
                LeetCodeCatalogProblem.objects.get_or_create(slug=sp["slug"], defaults=sp)

    @staticmethod
    def _persist_insights_and_recs(user, platform: str, payload: Dict[str, Any]):
        try:
            from insights.models import Insight
            from recommendations.models import Recommendation

            # Process insights items
            insights_raw = payload.get("insights")
            items = []
            if isinstance(insights_raw, dict) and "items" in insights_raw:
                items = insights_raw["items"]
            elif isinstance(insights_raw, list):
                items = insights_raw

            for item in items:
                if isinstance(item, dict) and "title" in item and "message" in item:
                    Insight.objects.get_or_create(
                        user=user,
                        title=item["title"],
                        defaults={
                            "type": item.get("type", "performance"),
                            "priority": item.get("priority", "medium"),
                            "message": item["message"],
                            "metadata": item.get("metadata", {"platform": platform}),
                        },
                    )

            # Process recommendations
            recs = payload.get("recommendations") or []
            for rec in recs:
                if isinstance(rec, str):
                    Recommendation.objects.get_or_create(
                        user=user,
                        title=f"{platform.capitalize()}: {rec[:60]}",
                        defaults={
                            "category": "platform",
                            "priority": "medium",
                            "description": rec,
                            "action": rec,
                            "estimated_time": 30,
                        },
                    )
        except Exception:
            pass

    @staticmethod
    def get_unified_analytics(user) -> Dict[str, Any]:
        """Unified Platform Analytics aggregating real-time metrics across all connected accounts."""
        connected_records = ConnectedPlatform.objects.filter(user=user, connected=True)
        platforms_payload = {}
        total_problems = 0
        total_repos = 0
        total_xp = 0
        languages: Dict[str, int] = {}
        difficulty_dist = {"Easy": 0, "Medium": 0, "Hard": 0}
        latest_sync = None

        for record in connected_records:
            platform_code = record.platform
            p_analytics = {}

            # Fast path: use cached analytics if already populated
            has_cache = bool(
                record.cached_analytics
                and isinstance(record.cached_analytics, dict)
                and (
                    record.cached_analytics.get("total_solved") is not None
                    or record.cached_analytics.get("problems_solved") is not None
                    or record.cached_analytics.get("solved_problems") is not None
                    or record.cached_analytics.get("badges") is not None
                    or record.cached_analytics.get("rating") is not None
                    or record.cached_analytics.get("total_repositories") is not None
                    or record.cached_analytics.get("total_xp") is not None
                )
            )

            if has_cache:
                p_analytics = record.cached_analytics
                platforms_payload[platform_code] = {
                    "connected": True,
                    "profile": {"username": record.username, "display_name": record.username, "available": True},
                    "analytics": p_analytics,
                    "insights": {},
                    "recommendations": [],
                }
            else:
                try:
                    connector = PlatformService.get_connector(
                        platform_code,
                        username=record.username,
                        access_token=record.get_access_token(),
                        refresh_token=record.get_refresh_token(),
                    )
                    analytics_data = connector.get_analytics()
                    if connector.username and connector.username != record.username:
                        record.username = connector.username
                        record.save(update_fields=["username", "updated_at"])

                    p_analytics = analytics_data.get("analytics") or {}
                    if p_analytics:
                        record.cached_analytics = p_analytics
                        record.last_synced_at = timezone.now()
                        record.save(update_fields=["cached_analytics", "last_synced_at", "updated_at"])

                    platforms_payload[platform_code] = {
                        "connected": True,
                        "profile": analytics_data.get("profile"),
                        "analytics": p_analytics,
                        "insights": analytics_data.get("insights"),
                        "recommendations": analytics_data.get("recommendations"),
                    }
                except Exception:
                    p_analytics = record.cached_analytics or {}
                    platforms_payload[platform_code] = {
                        "connected": True,
                        "profile": {"username": record.username, "available": False},
                        "analytics": p_analytics,
                        "insights": {},
                        "recommendations": [],
                    }

            # Aggregations
            if platform_code == "leetcode":
                solved = p_analytics.get("total_solved") or 0
                total_problems += int(solved)
                diff_data = p_analytics.get("difficulty_distribution") or {}
                for d_k, d_v in diff_data.items():
                    norm_k = d_k.capitalize()
                    if norm_k in difficulty_dist:
                        difficulty_dist[norm_k] += int(d_v or 0)
                if not diff_data and (p_analytics.get("easy_solved") or p_analytics.get("medium_solved") or p_analytics.get("hard_solved")):
                    difficulty_dist["Easy"] += int(p_analytics.get("easy_solved") or 0)
                    difficulty_dist["Medium"] += int(p_analytics.get("medium_solved") or 0)
                    difficulty_dist["Hard"] += int(p_analytics.get("hard_solved") or 0)
            elif platform_code in ["hackerrank", "codechef"]:
                solved = (
                    p_analytics.get("total_solved")
                    or p_analytics.get("problems_solved")
                    or p_analytics.get("solved_problems")
                    or p_analytics.get("challenges")
                    or 0
                )
                total_problems += int(solved)
            elif platform_code == "github":
                total_repos += int(p_analytics.get("total_repositories") or 0)
                lang_dist = p_analytics.get("language_distribution") or {}
                for l_k, l_v in lang_dist.items():
                    languages[l_k] = languages.get(l_k, 0) + int(l_v or 0)
            elif platform_code == "duolingo":
                total_xp += int(p_analytics.get("total_xp") or p_analytics.get("xp") or 0)

            if record.last_synced_at:
                if latest_sync is None or record.last_synced_at > latest_sync:
                    latest_sync = record.last_synced_at

        return {
            "total_problems_solved": total_problems,
            "total_repositories": total_repos,
            "total_language_xp": total_xp,
            "platforms_connected": connected_records.count(),
            "last_sync": latest_sync.isoformat() if latest_sync else None,
            "languages": languages,
            "difficulty_distribution": difficulty_dist,
            "platforms": platforms_payload,
        }
