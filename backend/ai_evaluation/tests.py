import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAIEvaluationAPI:
    def test_ai_evaluation_summary_returns_assessment(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="aieval@example.com",
            username="aieval",
            password="StrongPass123!",
            target_role="Backend Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/ai-evaluation/")

        assert response.status_code == 200
        payload = response.json()
        assert "overall_score" in payload
        assert "strengths" in payload
        assert "improvement_areas" in payload

    def test_ai_evaluation_submission_returns_result(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="aievalsubmit@example.com",
            username="aievalsubmit",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/ai-evaluation/",
            {
                "prompt": "Evaluate my interview readiness for a backend role.",
                "context": "I have solved 120 DSA problems and built two portfolio projects.",
            },
            format="json",
        )

        assert response.status_code == 200
        payload = response.json()
        assert "overall_score" in payload
        assert "summary" in payload
