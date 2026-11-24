from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from insights.models import Insight
from recommendations.models import Recommendation
from tasks.models import DailyTaskPlan


def _dashboard_payload_for_user(user):
    today_plan = DailyTaskPlan.objects.filter(user=user).order_by("-date").first()
    recent_recommendations = Recommendation.objects.filter(user=user).order_by("-created_at")[:3]
    recent_insights = Insight.objects.filter(user=user).order_by("-created_at")[:3]

    from progress.views import _active_days, _current_streak, _longest_streak
    active_days = _active_days(user)
    current_streak = _current_streak(active_days)
    longest_streak = _longest_streak(active_days)

    latest_interview = None
    try:
        from interviews.models import MockInterview
        latest_interview = (
            MockInterview.objects.filter(user=user, overall_score__isnull=False, status="completed")
            .order_by("-completed_at")
            .first()
        )
    except Exception:
        pass

    overview = {
        "user": user.email,
        "target_role": user.target_role or "Not set",
        "daily_study_hours": float(user.daily_study_hours or 0),
        "total_plans": DailyTaskPlan.objects.filter(user=user).count(),
        "active_recommendations": recent_recommendations.count(),
        "active_insights": recent_insights.count(),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }

    return {
        "overview": overview,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "latest_interview_score": latest_interview.overall_score if latest_interview else None,
        "daily_plan": {
            "date": getattr(today_plan, "date", None).isoformat() if today_plan and today_plan.date else None,
            "status": getattr(today_plan, "status", "planned") or "planned",
            "total_minutes": getattr(today_plan, "total_minutes", 0) or 0,
            "completed_minutes": getattr(today_plan, "completed_minutes", 0) or 0,
        },
        "recommendations": [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "priority": item.priority,
                "action": item.action,
            }
            for item in recent_recommendations
        ],
        "insights": [
            {
                "id": item.id,
                "title": item.title,
                "type": item.type,
                "priority": item.priority,
                "message": item.message,
            }
            for item in recent_insights
        ],
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    payload = _dashboard_payload_for_user(request.user)
    return Response(payload)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_update(request):
    payload = _dashboard_payload_for_user(request.user)
    return Response({
        "updated_at": timezone.now().isoformat(),
        "overview": payload["overview"],
        "daily_plan": payload["daily_plan"],
    })
