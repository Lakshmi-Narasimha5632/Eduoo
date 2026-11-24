import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestSkillGapAPI:
    def test_skill_gaps_summary_returns_gap_analysis(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="skillgaps@example.com",
            username="skillgaps",
            password="StrongPass123!",
            target_role="Backend Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/skill-gaps/")

        assert response.status_code == 200
        payload = response.json()
        assert "summary" in payload
        assert "skill_gaps" in payload
        assert "recommended_focus" in payload

    def test_skill_gap_creation_accepts_custom_gap(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="skillcreate@example.com",
            username="skillcreate",
            password="StrongPass123!",
            target_role="Full Stack Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/skill-gaps/",
            {
                "skill": "System Design",
                "severity": "high",
                "reason": "Needs stronger architecture practice",
            },
            format="json",
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["skill"] == "System Design"
        assert payload["severity"] == "high"
