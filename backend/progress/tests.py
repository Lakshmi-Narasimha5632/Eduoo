import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestProgressAPI:
    def test_progress_summary_returns_streak_and_totals(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="progress@example.com",
            username="progress",
            password="StrongPass123!",
            daily_study_hours=2,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/progress/")

        assert response.status_code == 200
        payload = response.json()
        assert "current_streak" in payload
        assert "longest_streak" in payload
        assert "total_tasks_completed" in payload
        assert "total_study_minutes" in payload

    def test_weekly_progress_endpoint_returns_week_data(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="weekly@example.com",
            username="weekly",
            password="StrongPass123!",
            daily_study_hours=2,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/progress/weekly/")

        assert response.status_code == 200
        payload = response.json()
        assert "week_start" in payload
        assert "week_end" in payload
        assert "summary" in payload
        assert "daily" in payload

    def test_streak_preserves_when_active_yesterday_not_yet_today(self, django_user_model):
        from datetime import timedelta
        from django.utils import timezone
        from tasks.models import DailyTask, DailyTaskPlan

        user = django_user_model.objects.create_user(
            email="streak_yesterday@example.com",
            username="streak_yesterday",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        yesterday = timezone.localdate() - timedelta(days=1)
        plan = DailyTaskPlan.objects.create(user=user, date=yesterday, status="completed", completed_minutes=45)
        DailyTask.objects.create(plan=plan, title="Solve Array problem", status="completed", estimated_minutes=45)

        res = client.get("/api/progress/")
        assert res.status_code == 200
        data = res.json()
        # Even though user hasn't completed today's task yet, yesterday's streak is preserved!
        assert data["current_streak"] == 1
        assert data["today_active"] is False

    def test_streak_increments_when_active_consecutive_days(self, django_user_model):
        from datetime import timedelta
        from django.utils import timezone
        from tasks.models import DailyTask, DailyTaskPlan

        user = django_user_model.objects.create_user(
            email="streak_multi@example.com",
            username="streak_multi",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        plan_yest = DailyTaskPlan.objects.create(user=user, date=yesterday, status="completed", completed_minutes=30)
        DailyTask.objects.create(plan=plan_yest, title="Task Yest", status="completed", estimated_minutes=30)

        plan_today = DailyTaskPlan.objects.create(user=user, date=today, status="completed", completed_minutes=30)
        DailyTask.objects.create(plan=plan_today, title="Task Today", status="completed", estimated_minutes=30)

        res = client.get("/api/progress/")
        assert res.status_code == 200
        data = res.json()
        assert data["current_streak"] == 2
        assert data["longest_streak"] == 2
        assert data["today_active"] is True

        # Check dashboard summary also returns 2
        dash_res = client.get("/api/dashboard/")
        assert dash_res.status_code == 200
        assert dash_res.json()["overview"]["current_streak"] == 2

    def test_streak_resets_to_zero_when_inactive_past_two_days(self, django_user_model):
        from datetime import timedelta
        from django.utils import timezone
        from tasks.models import DailyTask, DailyTaskPlan

        user = django_user_model.objects.create_user(
            email="streak_broken@example.com",
            username="streak_broken",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        two_days_ago = timezone.localdate() - timedelta(days=2)
        plan = DailyTaskPlan.objects.create(user=user, date=two_days_ago, status="completed", completed_minutes=30)
        DailyTask.objects.create(plan=plan, title="Old Task", status="completed", estimated_minutes=30)

        res = client.get("/api/progress/")
        assert res.status_code == 200
        data = res.json()
        assert data["current_streak"] == 0
        assert data["longest_streak"] == 1

    def test_longest_streak_historical_calculation(self, django_user_model):
        from datetime import timedelta
        from django.utils import timezone
        from tasks.models import DailyTask, DailyTaskPlan

        user = django_user_model.objects.create_user(
            email="streak_longest@example.com",
            username="streak_longest",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today = timezone.localdate()

        # 3 consecutive days in the past (days -6, -5, -4)
        for offset in [6, 5, 4]:
            d = today - timedelta(days=offset)
            plan = DailyTaskPlan.objects.create(user=user, date=d, status="completed", completed_minutes=30)
            DailyTask.objects.create(plan=plan, title=f"Task {offset}", status="completed", estimated_minutes=30)

        # Day -3 and Day -2 were missed.

        # Active yesterday and today (days -1, 0)
        for offset in [1, 0]:
            d = today - timedelta(days=offset)
            plan = DailyTaskPlan.objects.create(user=user, date=d, status="completed", completed_minutes=30)
            DailyTask.objects.create(plan=plan, title=f"Task {offset}", status="completed", estimated_minutes=30)

        res = client.get("/api/progress/")
        assert res.status_code == 200
        data = res.json()
        assert data["current_streak"] == 2
        assert data["longest_streak"] == 3
