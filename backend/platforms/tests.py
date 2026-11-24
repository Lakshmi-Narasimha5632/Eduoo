import pytest
from rest_framework.test import APIClient
from platforms.models import ConnectedPlatform, LeetCodeCatalogProblem


@pytest.mark.django_db
class TestPlatformAPI:
    def test_platforms_list_includes_all_supported_platforms(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="platform@example.com",
            username="platform",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/platforms/")

        assert response.status_code == 200
        payload = response.json()
        names = {item["platform"] for item in payload["platforms"]}
        assert {"leetcode", "github", "duolingo", "linkedin", "hackerrank", "codechef"}.issubset(names)

    def test_connect_platform_sets_connected_status(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="connect@example.com",
            username="connect",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/platforms/leetcode/connect/",
            {"username": "narasimha", "access_token": "demo-token"},
            format="json",
        )

        assert response.status_code == 201
        assert response.json()["platform"] == "leetcode"
        assert response.json()["connected"] is True
        assert response.json()["username"] == "narasimha"

    def test_sync_platform_enriches_payload(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="sync@example.com",
            username="sync",
            password="StrongPass123!",
        )
        ConnectedPlatform.objects.create(
            user=user,
            platform="leetcode",
            username="testuser",
            connected=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/platforms/leetcode/sync/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "payload" in response.json()
        assert response.json()["payload"]["platform"] == "leetcode"

    def test_unified_analytics_returns_connected_platforms(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="unified@example.com",
            username="unified",
            password="StrongPass123!",
        )
        ConnectedPlatform.objects.create(
            user=user,
            platform="github",
            username="testcoder",
            connected=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/platforms/unified/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "platforms" in response.json()
        assert "github" in response.json()["platforms"]

    def test_leetcode_catalog_endpoint(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="catalog@example.com",
            username="catalog",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/platforms/leetcode/catalog/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["count"] > 0
        assert any(p["slug"] == "two-sum" for p in response.json()["problems"])

    def test_disconnect_platform(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="disconnect@example.com",
            username="disconnect",
            password="StrongPass123!",
        )
        ConnectedPlatform.objects.create(
            user=user,
            platform="duolingo",
            username="polyglot",
            connected=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete("/api/platforms/duolingo/disconnect/")
        assert response.status_code == 200
        assert response.json()["connected"] is False

        record = ConnectedPlatform.objects.get(user=user, platform="duolingo")
        assert record.connected is False
