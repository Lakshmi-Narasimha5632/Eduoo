import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from tasks.models import DailyTaskPlan
from tasks.services import DailyTaskReportService


@pytest.mark.django_db
class TestTaskPlanner:
    def test_today_tasks_generates_a_daily_plan(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="tasks@example.com",
            username="tasks",
            password="StrongPass123!",
            daily_study_hours=2,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/tasks/today/")

        assert response.status_code == 200
        payload = response.json()["plan"]
        assert payload["total_minutes"] > 0
        assert len(payload["tasks"]) >= 2

    def test_complete_task_marks_task_completed(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="complete@example.com",
            username="complete",
            password="StrongPass123!",
            daily_study_hours=2,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today_plan = client.get("/api/tasks/today/").json()["plan"]
        task_id = today_plan["tasks"][0]["id"]

        response = client.post(f"/api/tasks/{task_id}/complete/")

        assert response.status_code == 200
        assert response.json()["task"]["status"] == "completed"

    def test_complete_all_tasks_triggers_automated_completion_report(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="report_user@example.com",
            username="report_user",
            password="StrongPass123!",
            daily_study_hours=1,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today_plan = client.get("/api/tasks/today/").json()["plan"]
        plan_id = today_plan["id"]

        # Complete all tasks in the plan
        for task in today_plan["tasks"]:
            client.post(f"/api/tasks/{task['id']}/complete/")

        plan = DailyTaskPlan.objects.get(id=plan_id)
        assert plan.status == "completed"
        assert plan.completion_report_sent is True
        assert plan.completion_report_sent_at is not None

    def test_incomplete_task_alert_dispatch(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="incomplete_user@example.com",
            username="incomplete_user",
            password="StrongPass123!",
            daily_study_hours=2,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today_plan = client.get("/api/tasks/today/").json()["plan"]
        plan = DailyTaskPlan.objects.get(id=today_plan["id"])

        res = DailyTaskReportService.send_incomplete_alert(plan, sync=True)
        assert res["success"] is True
        assert res["report_type"] == "incomplete_alert"
        assert res["recipient"] == user.email

        plan.refresh_from_db()
        assert plan.incomplete_alert_sent is True

    def test_send_daily_report_api_endpoint(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="endpoint_user@example.com",
            username="endpoint_user",
            password="StrongPass123!",
            daily_study_hours=1.5,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Trigger send-daily-report endpoint
        res = client.post("/api/tasks/send-daily-report/", {"force": True}, format="json")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["recipient"] == user.email

    def test_management_command_send_daily_task_reports(self, django_user_model):
        django_user_model.objects.create_user(
            email="mgmt_cmd@example.com",
            username="mgmt_cmd",
            password="StrongPass123!",
            daily_study_hours=2,
            is_email_verified=True,
        )

        # Run command without raising errors
        call_command("send_daily_task_reports", force=True, sync=True)

    def test_complete_task_prevents_double_counting(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="doublecount@example.com",
            username="doublecount",
            password="StrongPass123!",
            daily_study_hours=2,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today_plan = client.get("/api/tasks/today/").json()["plan"]
        task_id = today_plan["tasks"][0]["id"]

        res1 = client.post(f"/api/tasks/{task_id}/complete/")
        completed_minutes_1 = client.get("/api/tasks/today/").json()["plan"]["completed_minutes"]

        # Call complete again
        res2 = client.post(f"/api/tasks/{task_id}/complete/")
        completed_minutes_2 = client.get("/api/tasks/today/").json()["plan"]["completed_minutes"]

        assert completed_minutes_1 == completed_minutes_2

    def test_delete_task_removes_from_plan(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="deletetask@example.com",
            username="deletetask",
            password="StrongPass123!",
            daily_study_hours=2,
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        today_plan = client.get("/api/tasks/today/").json()["plan"]
        task_id = today_plan["tasks"][0]["id"]
        initial_count = len(today_plan["tasks"])

        res = client.delete(f"/api/tasks/{task_id}/")
        assert res.status_code == 200
        assert res.json()["success"] is True

        refreshed_plan = client.get("/api/tasks/today/").json()["plan"]
        assert len(refreshed_plan["tasks"]) == initial_count - 1

    def test_daily_tasks_change_day_by_day(self, django_user_model):
        from datetime import date
        user = django_user_model.objects.create_user(
            email="daily_change_user@example.com",
            username="daily_change_user",
            password="StrongPass123!",
            daily_study_hours=2,
            target_role="Full Stack Developer",
            is_email_verified=True,
        )
        day1 = date(2026, 11, 7)
        day2 = date(2026, 11, 8)
        day3 = date(2026, 11, 9)

        plan1 = DailyTaskReportService.get_or_create_plan(user, target_date=day1) if hasattr(DailyTaskReportService, 'get_or_create_plan') else None
        from tasks.planners import AdaptiveDailyTaskPlanner
        plan1 = AdaptiveDailyTaskPlanner.generate_for_user(user, target_date=day1)
        plan2 = AdaptiveDailyTaskPlanner.generate_for_user(user, target_date=day2)
        plan3 = AdaptiveDailyTaskPlanner.generate_for_user(user, target_date=day3)

        titles1 = set(plan1.tasks.values_list("title", flat=True))
        titles2 = set(plan2.tasks.values_list("title", flat=True))
        titles3 = set(plan3.tasks.values_list("title", flat=True))

        # Check that consecutive days do NOT produce identical tasks
        assert titles1 != titles2
        assert titles2 != titles3
        assert titles1 != titles3
