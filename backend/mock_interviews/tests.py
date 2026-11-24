import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestMockInterviewAPI:
    def test_mock_interviews_list_returns_questions(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="mock@example.com",
            username="mock",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/mock-interviews/")

        assert response.status_code == 200
        payload = response.json()
        assert "questions" in payload
        assert isinstance(payload["questions"], list)

    def test_mock_interview_submission_returns_feedback(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="mocksubmit@example.com",
            username="mocksubmit",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/mock-interviews/",
            {
                "question": "Explain your project architecture.",
                "answer": "I designed a modular backend with clear service boundaries and test coverage.",
            },
            format="json",
        )

        assert response.status_code == 200
        payload = response.json()
        assert "score" in payload
        assert "feedback" in payload
