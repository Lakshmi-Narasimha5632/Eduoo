import pytest
from rest_framework.test import APIClient
from notifications.models import Notification, NotificationPreference
from notifications.services import NotificationService


@pytest.mark.django_db
class TestNotificationsAPI:
    def test_notification_list_and_mark_read(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="notif@example.com",
            username="notif",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Create sample notification
        NotificationService.create_notification(
            user=user,
            title="Today's Tasks Ready",
            message="Your daily study plan for Full Stack Developer is ready.",
            category="task_reminder",
        )

        response = client.get("/api/notifications/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["notifications"]) == 1
        notif_id = response.json()["notifications"][0]["id"]

        # Mark read
        read_res = client.post("/api/notifications/read/", {"id": notif_id}, format="json")
        assert read_res.status_code == 200

        # Verify updated
        updated = Notification.objects.get(id=notif_id)
        assert updated.is_read is True

    def test_notification_preferences(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="prefs@example.com",
            username="prefs",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        get_res = client.get("/api/notifications/preferences/")
        assert get_res.status_code == 200
        assert get_res.json()["preferences"]["daily_task_reminders"] is True

        put_res = client.put(
            "/api/notifications/preferences/",
            {
                "preferences": {
                    "daily_task_reminders": False,
                    "streak_reminders": True,
                    "email_notifications": True,
                    "notification_email": "custom@example.com",
                }
            },
            format="json",
        )
        assert put_res.status_code == 200
        prefs_data = put_res.json()["preferences"]
        assert prefs_data["daily_task_reminders"] is False
        assert prefs_data["email_notifications"] is True
        assert prefs_data["notification_email"] == "custom@example.com"

    def test_test_email_endpoint(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="tester@example.com",
            username="tester",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        res = client.post("/api/notifications/test-email/", {"email": "tester@example.com"}, format="json")
        assert res.status_code == 200
        assert res.json()["success"] is True
        assert "tester@example.com" in res.json()["recipient"]
