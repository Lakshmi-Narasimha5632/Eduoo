from datetime import date, timedelta

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tasks.models import DailyTask, DailyTaskPlan


def _active_days(user):
    days = set()

    # 1. Plans with completed tasks
    for d in DailyTaskPlan.objects.filter(user=user, tasks__status="completed").values_list("date", flat=True):
        if d:
            days.add(d)

    # 2. Plans with completed study minutes > 0
    for d in DailyTaskPlan.objects.filter(user=user, completed_minutes__gt=0).values_list("date", flat=True):
        if d:
            days.add(d)

    # 3. Tasks with completed_at timestamp in local time
    for dt in DailyTask.objects.filter(plan__user=user, status="completed", completed_at__isnull=False).values_list("completed_at", flat=True):
        if dt:
            days.add(timezone.localtime(dt).date())

    # 4. StudyProgress records with activity
    try:
        from progress.models import StudyProgress
        for d in StudyProgress.objects.filter(user=user).filter(Q(tasks_completed__gt=0) | Q(study_minutes__gt=0)).values_list("date", flat=True):
            if d:
                days.add(d)
    except Exception:
        pass

    # 5. Completed Mock Interviews in local time
    try:
        from interviews.models import MockInterview
        for dt in MockInterview.objects.filter(user=user, status="completed", completed_at__isnull=False).values_list("completed_at", flat=True):
            if dt:
                days.add(timezone.localtime(dt).date())
    except Exception:
        pass

    # Normalize to datetime.date objects
    normalized = set()
    for d in days:
        if d is not None:
            if hasattr(d, "date") and callable(getattr(d, "date")) and hasattr(d, "hour"):
                normalized.add(d.date())
            else:
                normalized.add(d)

    return normalized


def _current_streak(active_days):
    if not active_days:
        return 0

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    # If active today, the streak starts today and counts backwards
    if today in active_days:
        start_day = today
    # If not active today, but active yesterday, streak is preserved from yesterday!
    elif yesterday in active_days:
        start_day = yesterday
    else:
        # Both today and yesterday inactive -> streak is broken
        return 0

    streak = 0
    current_day = start_day
    while current_day in active_days:
        streak += 1
        current_day -= timedelta(days=1)

    return streak


def _longest_streak(active_days):
    if not active_days:
        return 0

    ordered_days = sorted(active_days)
    if not ordered_days:
        return 0

    longest = 1
    current = 1

    for previous, current_day in zip(ordered_days, ordered_days[1:]):
        diff = (current_day - previous).days
        if diff == 1:
            current += 1
            longest = max(longest, current)
        elif diff > 1:
            current = 1

    cur = _current_streak(active_days)
    return max(longest, cur)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def progress_summary(request):
    user = request.user
    active_days = _active_days(user)
    today = timezone.localdate()
    cur_streak = _current_streak(active_days)
    long_streak = _longest_streak(active_days)
    total_tasks_completed = DailyTask.objects.filter(plan__user=user, status="completed").count()
    total_study_minutes = int(
        DailyTaskPlan.objects.filter(user=user).aggregate(total=Sum("completed_minutes"))["total"] or 0
    )

    return Response(
        {
            "current_streak": cur_streak,
            "longest_streak": long_streak,
            "today_active": today in active_days,
            "total_tasks_completed": total_tasks_completed,
            "total_study_minutes": total_study_minutes,
            "active_days": len(active_days),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def weekly_progress(request):
    user = request.user
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    active_days = _active_days(user)

    daily = []
    total_tasks_completed = 0
    total_study_minutes = 0

    for offset in range(7):
        current_day = week_start + timedelta(days=offset)
        tasks_completed = DailyTask.objects.filter(plan__user=user, plan__date=current_day, status="completed").count()
        study_minutes = int(
            DailyTaskPlan.objects.filter(user=user, date=current_day).aggregate(total=Sum("completed_minutes"))["total"] or 0
        )

        total_tasks_completed += tasks_completed
        total_study_minutes += study_minutes
        is_active = (current_day in active_days) or (tasks_completed > 0) or (study_minutes > 0)

        daily.append(
            {
                "date": current_day.isoformat(),
                "tasks_completed": tasks_completed,
                "study_minutes": study_minutes,
                "active": is_active,
            }
        )

    return Response(
        {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "summary": {
                "days_active": sum(1 for item in daily if item["active"]),
                "total_tasks_completed": total_tasks_completed,
                "total_study_minutes": total_study_minutes,
            },
            "daily": daily,
        }
    )
