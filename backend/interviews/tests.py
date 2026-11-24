import pytest
from rest_framework.test import APIClient
from interviews.models import MockInterview, InterviewQuestion, InterviewAnswer


@pytest.mark.django_db
class TestInterviewsAPI:
    def test_start_interview_creates_session_and_first_question(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="candidate@example.com",
            username="candidate",
            password="StrongPass123!",
            target_role="Full Stack Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/interviews/",
            {"interview_type": "technical", "difficulty": "intermediate", "duration_minutes": 30},
            format="json",
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["success"] is True
        assert "interview" in payload
        assert len(payload["interview"]["questions"]) >= 1
        assert payload["interview"]["target_role"] == "Full Stack Developer"

    def test_answer_question_evaluates_and_returns_next_question(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="interviewee@example.com",
            username="interviewee",
            password="StrongPass123!",
            target_role="Backend Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Start interview
        start_res = client.post("/api/interviews/", {"interview_type": "technical"}, format="json")
        interview_id = start_res.json()["interview"]["id"]

        # Submit answer
        answer_payload = {
            "answer": "I built a distributed caching layer using Redis and Django REST framework. We indexed primary lookup keys and achieved a 40% reduction in p95 query latency."
        }
        ans_res = client.post(f"/api/interviews/{interview_id}/answer/", answer_payload, format="json")

        assert ans_res.status_code == 200
        data = ans_res.json()
        assert data["success"] is True
        assert "evaluation" in data
        assert data["evaluation"]["score"] > 0
        assert "next_question" in data
        assert data["next_question"]["order"] == 2

    def test_chat_with_ai_interviewer_and_message_stream(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="chatbot_user@example.com",
            username="chatbot_user",
            password="StrongPass123!",
            target_role="Cloud Architect",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        start_res = client.post("/api/interviews/", {"interview_type": "technical", "target_role": "Cloud Architect"}, format="json")
        assert start_res.status_code == 201
        interview_id = start_res.json()["interview"]["id"]

        detail_res = client.get(f"/api/interviews/{interview_id}/")
        assert detail_res.status_code == 200
        messages = detail_res.json().get("messages", [])
        assert len(messages) >= 2
        assert messages[0]["sender"] == "agent"
        assert messages[0]["message_type"] == "greeting"
        assert messages[1]["message_type"] == "question"

        clarify_res = client.post(
            f"/api/interviews/{interview_id}/chat/",
            {"message": "Can I assume AWS or GCP multi-region architecture?", "mode": "clarify"},
            format="json",
        )
        assert clarify_res.status_code == 200
        clarify_data = clarify_res.json()
        assert clarify_data["success"] is True
        assert "agent_response" in clarify_data

        chat_ans_res = client.post(
            f"/api/interviews/{interview_id}/chat/",
            {
                "message": "We would deploy an active-active multi-region Kubernetes cluster with DynamoDB Global Tables and AWS Route 53 latency-based routing.",
                "mode": "answer",
            },
            format="json",
        )
        assert chat_ans_res.status_code == 200
        ans_data = chat_ans_res.json()
        assert ans_data["success"] is True
        assert "evaluation" in ans_data
        assert ans_data["evaluation"]["score"] > 0

    def test_finish_interview_and_result_report(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="eval@example.com",
            username="eval",
            password="StrongPass123!",
            target_role="Python Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        start_res = client.post("/api/interviews/", {}, format="json")
        interview_id = start_res.json()["interview"]["id"]

        client.post(
            f"/api/interviews/{interview_id}/answer/",
            {"answer": "Python uses reference counting and a cyclic garbage collector. In production we tune memory leaks using objgraph and tracemalloc."},
            format="json",
        )

        finish_res = client.post(f"/api/interviews/{interview_id}/finish/")
        assert finish_res.status_code == 200
        result = finish_res.json()["result"]
        assert result["overall_score"] > 0
        assert "scores" in result
        assert "strengths" in result

        report_res = client.get(f"/api/interviews/{interview_id}/result/")
        assert report_res.status_code == 200
        assert report_res.json()["result"]["interview_id"] == interview_id

    def test_custom_question_count_honored_and_stops_at_limit(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="count_test@example.com",
            username="count_test",
            password="StrongPass123!",
            target_role="Frontend Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Start interview with custom question count of 2
        start_res = client.post(
            "/api/interviews/",
            {"interview_type": "technical", "num_questions": 2},
            format="json",
        )
        assert start_res.status_code == 201
        interview_payload = start_res.json()["interview"]
        assert interview_payload["num_questions"] == 2
        assert interview_payload["target_questions_count"] == 2
        interview_id = interview_payload["id"]

        # Detail view check
        detail_res = client.get(f"/api/interviews/{interview_id}/")
        assert detail_res.status_code == 200
        assert detail_res.json()["num_questions"] == 2

        # Answer Q1 -> should produce Q2
        q1_res = client.post(
            f"/api/interviews/{interview_id}/answer/",
            {"answer": "React uses a virtual DOM to diff updates in memory before applying minimal mutations to the real DOM."},
            format="json",
        )
        assert q1_res.status_code == 200
        q1_data = q1_res.json()
        assert q1_data["is_complete"] is False
        assert q1_data["next_question"] is not None
        assert q1_data["next_question"]["order"] == 2

        # Answer Q2 -> should complete session because limit is 2 (NOT continue to 5)
        q2_res = client.post(
            f"/api/interviews/{interview_id}/answer/",
            {"answer": "I use useMemo, useCallback, and React.memo alongside TanStack Query caching to prevent redundant re-renders."},
            format="json",
        )
        assert q2_res.status_code == 200
        q2_data = q2_res.json()
        assert q2_data["is_complete"] is True
        assert q2_data["is_finished"] is True
        assert q2_data["next_question"] is None

        # Confirm interview has exactly 2 questions created in DB
        interview_obj = MockInterview.objects.get(id=interview_id)
        assert interview_obj.questions.count() == 2
        assert interview_obj.status == "completed"

        # Check scorecard reports 2/2 evaluated
        result_res = client.get(f"/api/interviews/{interview_id}/result/")
        assert result_res.status_code == 200
        result_data = result_res.json()["result"]
        assert result_data["total_questions"] == 2
        assert result_data["questions_answered"] == 2

    def test_ai_agent_persona_selection_and_interaction(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="agent_test@example.com",
            username="agent_test",
            password="StrongPass123!",
            target_role="AI Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Start interview with specific AI agent persona
        start_res = client.post(
            "/api/interviews/",
            {
                "interview_type": "technical",
                "agent_persona": "sophia_algorithms",
                "agent_strictness": "rigorous",
                "num_questions": 3,
            },
            format="json",
        )
        assert start_res.status_code == 201
        interview = start_res.json()["interview"]
        assert interview["agent_persona"] == "sophia_algorithms"
        assert interview["agent_details"]["name"] == "Dr. Sophia Lin"
        interview_id = interview["id"]

        # Request a hint from the AI Agent
        hint_res = client.post(
            f"/api/interviews/{interview_id}/agent-interaction/",
            {"type": "hint", "message": "Could you provide a hint for the optimal time complexity?"},
            format="json",
        )
        assert hint_res.status_code == 200
        hint_data = hint_res.json()
        assert hint_data["success"] is True
        assert "agent_response" in hint_data
        assert len(hint_data["agent_response"]) > 10
        assert hint_data["agent"]["id"] == "sophia_algorithms"

        # Ask a clarifying question to the AI Agent
        clarify_res = client.post(
            f"/api/interviews/{interview_id}/clarify/",
            {"message": "Can I assume memory fits in RAM?"},
            format="json",
        )
        assert clarify_res.status_code == 200
        clarify_data = clarify_res.json()
        assert clarify_data["success"] is True
        assert "agent_response" in clarify_data

        # Submit answer and finish
        client.post(
            f"/api/interviews/{interview_id}/answer/",
            {"answer": "We maintain a sliding window invariant with a hash map to track counts in O(n) time."},
            format="json",
        )
        finish_res = client.post(f"/api/interviews/{interview_id}/finish/")
        assert finish_res.status_code == 200
        result = finish_res.json()["result"]
        assert result["agent_details"]["name"] == "Dr. Sophia Lin"
        assert "Sophia" in result["agent_assessment"]

    def test_distinct_questions_across_agents_and_round_types(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="diverse@example.com",
            username="diverse",
            password="StrongPass123!",
            target_role="Software Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # 1. Alex Chen - System Design
        res_alex = client.post(
            "/api/interviews/",
            {"agent_persona": "alex_architect", "interview_type": "system_design", "target_role": "Backend Engineer"},
            format="json",
        )
        q1_alex = res_alex.json()["interview"]["questions"][0]["question"]

        # 2. Sophia Lin - Coding
        res_sophia = client.post(
            "/api/interviews/",
            {"agent_persona": "sophia_algorithms", "interview_type": "coding", "target_role": "Frontend Developer"},
            format="json",
        )
        q1_sophia = res_sophia.json()["interview"]["questions"][0]["question"]

        # 3. Marcus Vance - Behavioral
        res_marcus = client.post(
            "/api/interviews/",
            {"agent_persona": "marcus_director", "interview_type": "behavioral", "target_role": "Product Manager"},
            format="json",
        )
        q1_marcus = res_marcus.json()["interview"]["questions"][0]["question"]

        # 4. Elena Rostova - Technical
        res_elena = client.post(
            "/api/interviews/",
            {"agent_persona": "elena_fullstack", "interview_type": "technical", "target_role": "Full Stack Developer"},
            format="json",
        )
        q1_elena = res_elena.json()["interview"]["questions"][0]["question"]

        # Assert all 4 are completely distinct and reflect their agent individuality!
        assert "Alex Chen" in q1_alex
        assert "Dr. Sophia Lin" in q1_sophia
        assert "Marcus Vance" in q1_marcus
        assert "Elena Rostova" in q1_elena
        assert len({q1_alex, q1_sophia, q1_marcus, q1_elena}) == 4

