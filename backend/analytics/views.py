"""Analytics views aggregating platform, study, and insight metrics."""

from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.constants import SUPPORTED_PLATFORMS, PLATFORM_CHOICES
from insights.models import Insight
from platforms.models import ConnectedPlatform
from platforms.services import PlatformService
from tasks.models import DailyTask, DailyTaskPlan


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    user = request.user
    total_tasks_completed = DailyTask.objects.filter(plan__user=user, status="completed").count()
    total_study_minutes = int(
        DailyTaskPlan.objects.filter(user=user).aggregate(total=Sum("completed_minutes"))["total"] or 0
    )
    active_platforms = ConnectedPlatform.objects.filter(user=user, connected=True).count()
    recent_insights = Insight.objects.filter(user=user).order_by("-created_at")[:5]

    platform_statuses = []
    for code, name in PLATFORM_CHOICES:
        obj = ConnectedPlatform.objects.filter(user=user, platform=code).first()
        platform_statuses.append({
            "platform": code,
            "display_name": name,
            "connected": obj.connected if obj else False,
            "username": obj.username if obj else None,
            "last_synced_at": obj.last_synced_at.isoformat() if (obj and obj.last_synced_at) else None,
        })

    return Response({
        "success": True,
        "overview": {
            "total_tasks_completed": total_tasks_completed,
            "total_study_minutes": total_study_minutes,
            "active_platforms": active_platforms,
            "daily_target_hours": float(user.daily_study_hours or 0),
        },
        "platforms": platform_statuses,
        "insights": [
            {
                "id": item.id,
                "type": item.type,
                "title": item.title,
                "priority": item.priority,
                "message": item.message,
            }
            for item in recent_insights
        ],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def platform_analytics(request, platform):
    if platform not in SUPPORTED_PLATFORMS:
        return Response(
            {"success": False, "error": {"code": "INVALID_PLATFORM", "message": "Unsupported platform."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    record = ConnectedPlatform.objects.filter(user=request.user, platform=platform).first()
    if not record or not record.connected or not record.username:
        return Response({
            "success": True,
            "platform": platform,
            "connected": False,
            "username": record.username if record else None,
            "metrics": {
                "total_solved": None,
                "easy_solved": None,
                "medium_solved": None,
                "hard_solved": None,
                "ranking": None,
                "activity_today": None,
                "activity_last_7_days": None,
                "activity_last_30_days": None,
                "consistency": None,
            },
        })

    try:
        connector = PlatformService.get_connector(
            platform,
            username=record.username,
            access_token=record.get_access_token(),
            refresh_token=record.get_refresh_token(),
        )
        analytics_result = connector.get_analytics()
        metrics = analytics_result.get("analytics") or {}
    except Exception:
        metrics = {}

    return Response({
        "success": True,
        "platform": platform,
        "connected": True,
        "username": record.username,
        "metrics": metrics,
    })
