import pytest
from rest_framework.test import APIClient
from skills.models import Skill, UserSkill
from skills.services import SkillService


@pytest.mark.django_db
class TestSkillsAPI:
    def test_skills_catalog_list(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="skills@example.com",
            username="skills",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/skills/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["skills"]) > 0

    def test_skill_gap_analysis(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="gaps@example.com",
            username="gaps",
            password="StrongPass123!",
            target_role="Full Stack Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/skills/gaps/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["target_role"] == "Full Stack Developer"
        assert "strong_skills" in payload
        assert "weak_skills" in payload
        assert "missing_skills" in payload
        assert "recommended_learning_path" in payload

    def test_career_readiness_calculation(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="readiness@example.com",
            username="readiness",
            password="StrongPass123!",
            target_role="Backend Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/skills/career-readiness/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert "overall_readiness" in payload
        assert payload["overall_readiness"] > 0
        assert "scores" in payload
        assert "factors" in payload
        assert len(payload["factors"]) == 6
