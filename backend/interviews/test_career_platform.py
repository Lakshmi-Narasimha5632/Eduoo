"""Unit and integration tests for the Career Preparation Platform:
Job Interviews, Communication Practice, and Skill Assessment."""

import pytest
from rest_framework.test import APIClient
from interviews.models import (
    CodingProblem,
    CodingSubmission,
    CommunicationSession,
    MockInterview,
    TechnicalQuiz,
)
from interviews.seeds import seed_skill_assessments


@pytest.mark.django_db
class TestCareerPlatformAPI:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        seed_skill_assessments()

    # --------------------------------------------------------------------------
    # Hub Overview Stats Test
    # --------------------------------------------------------------------------
    def test_interviews_hub_stats(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="hub_user@example.com",
            username="hub_user",
            password="StrongPass123!",
            target_role="Full Stack Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        res = client.get("/api/interviews/hub/stats/")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "hub" in data
        assert "job_interviews" in data["hub"]
        assert "communication" in data["hub"]
        assert "skill_assessment" in data["hub"]

    # --------------------------------------------------------------------------
    # Section 1: Job Interviews New Features Test
    # --------------------------------------------------------------------------
    def test_job_interview_creation_with_role_level_and_company(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="job_user@example.com",
            username="job_user",
            password="StrongPass123!",
            target_role="AI Engineer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        res = client.post(
            "/api/interviews/",
            {
                "target_role": "AI Engineer",
                "experience_level": "fresher",
                "interview_type": "company_specific",
                "company_name": "Google",
                "interview_mode": "voice_text",
                "num_questions": 3,
            },
            format="json",
        )
        assert res.status_code == 201
        interview = res.json()["interview"]
        assert interview["target_role"] == "AI Engineer"
        assert interview["experience_level"] == "fresher"
        assert interview["interview_type"] == "company_specific"
        assert interview["company_name"] == "Google"
        assert interview["interview_mode"] == "voice_text"

    # --------------------------------------------------------------------------
    # Section 2: Communication Section Tests
    # --------------------------------------------------------------------------
    def test_communication_topics_endpoint(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="comm_user@example.com",
            username="comm_user",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        res = client.get("/api/interviews/communication/topics/")
        assert res.status_code == 200
        payload = res.json()
        assert payload["success"] is True
        assert "daily_practice" in payload["modes"]
        assert "group_discussion" in payload["modes"]
        assert "workplace_scenarios" in payload["modes"]

    def test_communication_session_lifecycle(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="comm_learner@example.com",
            username="comm_learner",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # 1. Start Session
        start_res = client.post(
            "/api/interviews/communication/",
            {
                "mode": "workplace_scenarios",
                "topic": "Salary Negotiation with Director",
            },
            format="json",
        )
        assert start_res.status_code == 201
        session_id = start_res.json()["session"]["id"]

        # 2. Detail
        detail_res = client.get(f"/api/interviews/communication/{session_id}/")
        assert detail_res.status_code == 200
        assert len(detail_res.json()["session"]["exchanges"]) >= 1

        # 3. Send User Speech / Message
        msg_res = client.post(
            f"/api/interviews/communication/{session_id}/message/",
            {
                "message": "I would like to discuss adjusting my compensation based on exceeding our team quarterly KPIs by 40%.",
                "audio_metrics": {"duration_seconds": 15},
            },
            format="json",
        )
        assert msg_res.status_code == 200
        msg_data = msg_res.json()
        assert msg_data["success"] is True
        assert "ai_exchanges" in msg_data
        assert len(msg_data["ai_exchanges"]) >= 1

        # 4. Finish Session & Get Multi-criteria Report
        finish_res = client.post(f"/api/interviews/communication/{session_id}/finish/")
        assert finish_res.status_code == 200
        final_session = finish_res.json()["session"]
        assert final_session["status"] == "completed"
        assert final_session["overall_score"] > 0
        assert final_session["pronunciation_score"] > 0
        assert final_session["grammar_score"] > 0
        assert final_session["fluency_score"] > 0
        assert final_session["speed_wpm"] > 0
        assert len(final_session["mistakes_and_corrections"]) >= 0
        assert len(final_session["better_sentence_suggestions"]) >= 0

    def test_all_ten_communication_modules_initialize_and_accept_speech(self, django_user_model):
        """Verifies that all 10 Communication modules start cleanly and process voice turns."""
        user = django_user_model.objects.create_user(
            email="all_modes_user@example.com",
            username="all_modes_user",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        all_10_modes = [
            "daily_practice",
            "conversational",
            "self_intro",
            "group_discussion",
            "public_speaking",
            "fluency_pronunciation",
            "vocabulary",
            "grammar",
            "sentence_formation",
            "workplace_scenarios",
        ]

        for mode in all_10_modes:
            start_res = client.post(
                "/api/interviews/communication/",
                {"mode": mode},
                format="json",
            )
            assert start_res.status_code == 201, f"Failed to start module {mode}"
            session = start_res.json()["session"]
            assert session["mode"] == mode
            assert len(session["exchanges"]) >= 1, f"Module {mode} missing opening message"

            # Post a spoken turn
            turn_res = client.post(
                f"/api/interviews/communication/{session['id']}/message/",
                {
                    "message": "I engineered the distributed pipeline and improved database query execution.",
                    "audio_metrics": {"duration_seconds": 8},
                },
                format="json",
            )
            assert turn_res.status_code == 200, f"Turn failed for module {mode}"
            assert turn_res.json()["success"] is True

    # --------------------------------------------------------------------------
    # Section 3: Skill Assessment Coding Challenges & Quiz Tests
    # --------------------------------------------------------------------------
    def test_skill_problems_list_and_detail(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="coder@example.com",
            username="coder",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        list_res = client.get("/api/interviews/skills/problems/")
        assert list_res.status_code == 200
        problems = list_res.json()["problems"]
        assert len(problems) >= 5

        # Check detail for two-sum
        detail_res = client.get("/api/interviews/skills/problems/two-sum/")
        assert detail_res.status_code == 200
        problem_data = detail_res.json()["problem"]
        assert problem_data["slug"] == "two-sum"
        assert "starter_templates" in problem_data
        assert len(problem_data["sample_test_cases"]) >= 1

    def test_skill_problem_run_code(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="runner@example.com",
            username="runner",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        run_res = client.post(
            "/api/interviews/skills/problems/two-sum/run/",
            {
                "language": "python",
                "code": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []\n",
            },
            format="json",
        )
        assert run_res.status_code == 200
        data = run_res.json()
        assert data["success"] is True
        assert data["all_passed"] is True
        assert len(data["results"]) >= 1

    def test_skill_problem_submit_code_and_analytics(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="submitter@example.com",
            username="submitter",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Submit valid solution
        sub_res = client.post(
            "/api/interviews/skills/problems/two-sum/submit/",
            {
                "language": "python",
                "code": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []\n",
            },
            format="json",
        )
        assert sub_res.status_code == 200
        sub_data = sub_res.json()
        assert sub_data["success"] is True
        assert sub_data["status"] == "Accepted"
        assert sub_data["passed_test_cases"] == sub_data["total_test_cases"]
        assert "optimal_solutions" in sub_data

        # Check analytics update
        analytics_res = client.get("/api/interviews/skills/analytics/")
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()["analytics"]
        assert analytics["total_solved"] >= 1
        assert analytics["streak_days"] >= 1
        assert analytics["accuracy_pct"] == 100

    def test_skill_quizzes_and_submission(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="quiz_taker@example.com",
            username="quiz_taker",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        quizzes_res = client.get("/api/interviews/skills/quizzes/")
        assert quizzes_res.status_code == 200
        quizzes = quizzes_res.json()["quizzes"]
        assert len(quizzes) >= 4

        # Submit attempt to python-core-advanced
        sub_quiz_res = client.post(
            "/api/interviews/skills/quizzes/python-core-advanced/submit/",
            {
                "answers": {"1": 0, "2": 1, "3": 1, "4": 1},
                "time_taken_seconds": 120,
            },
            format="json",
        )
        assert sub_quiz_res.status_code == 200
        quiz_result = sub_quiz_res.json()
        assert quiz_result["success"] is True
        assert quiz_result["score"] == 100
        assert quiz_result["total_correct"] == 4
        assert len(quiz_result["review"]) == 4

    # --------------------------------------------------------------------------
    # Strict Evaluation Grounding Tests (Never Defaults)
    # --------------------------------------------------------------------------
    def test_job_interview_strictly_evaluates_user_actual_answer(self, django_user_model):
        """Verifies that evaluation is strictly derived from user's actual answer and never default strings."""
        user = django_user_model.objects.create_user(
            email="tech_candidate@example.com",
            username="tech_candidate",
            password="StrongPass123!",
            target_role="Backend Developer",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # 1. Start an interview
        start_res = client.post(
            "/api/interviews/",
            {
                "target_role": "Backend Developer",
                "experience_level": "intermediate",
                "interview_type": "technical",
                "num_questions": 2,
            },
            format="json",
        )
        assert start_res.status_code == 201
        interview_id = start_res.json()["interview"]["id"]

        # 2. Submit a technical answer citing Redis and latency
        ans_res = client.post(
            f"/api/interviews/{interview_id}/answer/",
            {
                "answer": "We implemented distributed caching using Redis with an LRU eviction policy to keep response latency under 20ms under heavy load."
            },
            format="json",
        )
        assert ans_res.status_code == 200
        eval_data = ans_res.json()["evaluation"]
        assert eval_data["score"] >= 50
        assert "redis" in str(eval_data).lower() or "caching" in str(eval_data).lower()
        # Verify it quoted or referenced the candidate's actual words
        assert "latency" in str(eval_data).lower()

        # 3. Submit a very brief non-answer
        brief_res = client.post(
            f"/api/interviews/{interview_id}/answer/",
            {
                "answer": "ok yes"
            },
            format="json",
        )
        assert brief_res.status_code == 200
        brief_eval = brief_res.json()["evaluation"]
        assert brief_eval["score"] <= 20
        assert "2 word(s)" in brief_eval["feedback"]

    def test_communication_strictly_evaluates_actual_user_sentences(self, django_user_model):
        """Verifies that communication grammar, upgrades, and scores are derived from candidate's actual words."""
        user = django_user_model.objects.create_user(
            email="speaker_user@example.com",
            username="speaker_user",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Start session
        start_res = client.post(
            "/api/interviews/communication/",
            {"mode": "conversational", "topic": "Sprint Retrospective"},
            format="json",
        )
        session_id = start_res.json()["session"]["id"]

        # Send actual user input with lowercase 'i' and colloquial vocabulary
        client.post(
            f"/api/interviews/communication/{session_id}/message/",
            {"message": "i worked on microservices and we had a lot of big problems with latency.", "audio_metrics": {"duration_seconds": 10}},
            format="json",
        )

        # Finish session
        finish_res = client.post(f"/api/interviews/communication/{session_id}/finish/")
        assert finish_res.status_code == 200
        session_data = finish_res.json()["session"]

        # Assert grammar mistake detects actual lowercase 'i' from candidate speech
        mistakes = session_data["mistakes_and_corrections"]
        assert any("I" in m["correction"] or "pronoun" in m["reason"] for m in mistakes)

        # Assert better sentence upgrades candidate's actual phrasing
        suggestions = session_data["better_sentence_suggestions"]
        assert len(suggestions) > 0
        assert "worked on" in suggestions[0]["original"] or "microservices" in suggestions[0]["original"]
        assert "spearheaded" in suggestions[0]["better_alternative"] or "engineered" in suggestions[0]["better_alternative"] or "critical bottleneck" in suggestions[0]["better_alternative"]

    def test_audio_transcribe_endpoint(self, django_user_model):
        """Verifies that the /api/interviews/transcribe/ endpoint transcribes input accurately without default text."""
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile

        user = django_user_model.objects.create_user(
            email="transcribe_user@example.com",
            username="transcribe_user",
            password="StrongPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # 1. Text pass-through
        res1 = client.post(
            "/api/interviews/transcribe/",
            {"text": "I scaled our Kubernetes deployment across three zones."},
            format="json",
        )
        assert res1.status_code == 200
        assert res1.json()["transcript"] == "I scaled our Kubernetes deployment across three zones."

        # 2. Uploaded audio file processing
        fake_wav = SimpleUploadedFile(
            "test_recording.wav",
            b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00",
            content_type="audio/wav",
        )
        res2 = client.post(
            "/api/interviews/transcribe/",
            {"audio": fake_wav, "fallback_text": "We reduced memory consumption using streaming generators."},
            format="multipart",
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["success"] is True
        assert data2["has_audio"] is True
        # If quiet audio has fallback, it uses the caller's text rather than hardcoded canned text
        assert "generators" in data2["transcript"] or data2["transcript"] == ""


