import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestResumeAPI:
    def test_resume_overview_returns_profile_and_strengths(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="resume@example.com",
            username="resume",
            password="StrongPass123!",
            full_name="Jane Doe",
            target_role="Backend Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/resume/")

        assert response.status_code == 200
        payload = response.json()
        assert "profile" in payload
        assert "strengths" in payload
        assert "skill_gaps" in payload

    def test_resume_update_endpoint_persists_changes(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="resumeupdate@example.com",
            username="resumeupdate",
            password="StrongPass123!",
            full_name="John Smith",
            target_role="Frontend Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/resume/",
            {"target_role": "Full Stack Engineer"},
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.target_role == "Full Stack Engineer"

    def test_resume_ats_analysis(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="ats@example.com",
            username="ats",
            password="StrongPass123!",
            target_role="Software Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/resume/analyze/",
            {"target_role": "Backend Developer"},
            format="json",
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert "ats_score" in payload
        assert "target_role_alignment" in payload
        assert "recommendations" in payload

    def test_resume_edit_parsed_data(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="editparsed@example.com",
            username="editparsed",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.put(
            "/api/resume/parsed/",
            {"skills": ["Python", "Django", "PostgreSQL", "Docker", "REST APIs"]},
            format="json",
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert "Python" in payload["parsed_data"]["skills"]
