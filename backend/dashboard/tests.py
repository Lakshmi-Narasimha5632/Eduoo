import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestDashboardAPI:
    def test_dashboard_summary_returns_key_sections(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="dashboard@example.com",
            username="dashboard",
            password="StrongPass123!",
            target_role="Backend Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/dashboard/")

        assert response.status_code == 200
        payload = response.json()
        assert "overview" in payload
        assert "daily_plan" in payload
        assert "recommendations" in payload
        assert "insights" in payload

    def test_dashboard_update_route_returns_recent_summary(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="dashboardupdate@example.com",
            username="dashboardupdate",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/dashboard/update/")

        assert response.status_code == 200
        payload = response.json()
        assert "updated_at" in payload
        assert "overview" in payload
