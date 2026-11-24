"""Platforms URL routing."""

from django.urls import path
from insights.views import generate_insights_view, insights_list
from recommendations.views import generate_recommendations_view, recommendations_list
from .views import (
    connect_platform,
    disconnect_platform,
    leetcode_catalog_view,
    linkedin_auth_url_view,
    linkedin_callback_view,
    platform_list,
    sync_all_platforms_view,
    sync_platform,
    unified_analytics_view,
)

urlpatterns = [
    path("", platform_list, name="platform-list"),
    path("sync-all/", sync_all_platforms_view, name="platform-sync-all"),
    path("unified/", unified_analytics_view, name="platform-unified"),
    path("leetcode/catalog/", leetcode_catalog_view, name="leetcode-catalog"),
    path("linkedin/auth-url/", linkedin_auth_url_view, name="linkedin-auth-url"),
    path("linkedin/callback/", linkedin_callback_view, name="linkedin-callback"),
    path("insights/", insights_list, name="platforms-insights-alias"),
    path("insights/generate/", generate_insights_view, name="platforms-insights-generate-alias"),
    path("recommendations/", recommendations_list, name="platforms-recommendations-alias"),
    path("recommendations/generate/", generate_recommendations_view, name="platforms-recommendations-generate-alias"),
    path("<slug:platform>/connect/", connect_platform, name="platform-connect"),
    path("<slug:platform>/sync/", sync_platform, name="platform-sync"),
    path("<slug:platform>/disconnect/", disconnect_platform, name="platform-disconnect"),
]
