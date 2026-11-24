import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAnalyticsAPI:
    def test_dashboard_summary_returns_key_metrics(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="analytics@example.com",
            username="analytics",
            password="StrongPass123!",
            daily_study_hours=2,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/analytics/")

        assert response.status_code == 200
        payload = response.json()
        assert "overview" in payload
        assert "platforms" in payload
        assert "insights" in payload

    def test_leetcode_analytics_endpoint_returns_metrics(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="leetcodeanalytics@example.com",
            username="leetcodeanalytics",
            password="StrongPass123!",
            daily_study_hours=2,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/analytics/leetcode/")

        assert response.status_code == 200
        payload = response.json()
        assert "platform" in payload
        assert "metrics" in payload
