"""API views for Job Interviews, Communication Practice, and Skill Assessment platform."""

from __future__ import annotations

import datetime
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .code_executor import CodeExecutionService
from .communication_service import CommunicationService
from .models import (
    CodingProblem,
    CodingSubmission,
    CommunicationSession,
    InterviewAnswer,
    InterviewChatMessage,
    InterviewQuestion,
    MockInterview,
    ProblemTestCase,
    QuizAttempt,
    TechnicalQuiz,
)
from .serializers import (
    CodingProblemDetailSerializer,
    CodingProblemListSerializer,
    CodingSubmissionSerializer,
    CommunicationSessionDetailSerializer,
    CommunicationSessionSerializer,
    MockInterviewSerializer,
    QuizAttemptSerializer,
    TechnicalQuizSerializer,
)
from .services import MockInterviewService


# ==============================================================================
# SECTION 1: JOB INTERVIEWS API VIEWS
# ==============================================================================

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def interview_list_create_view(request):
    user = request.user
    if request.method == "POST":
        raw_role = request.data.get("target_role") or request.data.get("role") or user.target_role or "Software Developer"
        target_role = str(raw_role).strip()
        interview_type = request.data.get("interview_type", "technical")
        experience_level = request.data.get("experience_level", "intermediate")
        company_name = str(request.data.get("company_name", "")).strip()
        interview_mode = request.data.get("interview_mode", "voice_text")
        difficulty = request.data.get("difficulty", "intermediate")
        duration = int(request.data.get("duration_minutes") or 30)

        raw_count = (
            request.data.get("num_questions")
            or request.data.get("target_questions_count")
            or request.data.get("question_count")
            or request.data.get("questions_count")
            or 5
        )
        try:
            num_questions = max(1, min(20, int(raw_count)))
        except (ValueError, TypeError):
            num_questions = 5

        agent_persona = request.data.get("agent_persona") or request.data.get("agent") or "alex_architect"
        agent_strictness = request.data.get("agent_strictness") or "balanced"

        interview = MockInterviewService.start_interview(
            user=user,
            target_role=target_role,
            interview_type=interview_type,
            difficulty=difficulty,
            duration_minutes=duration,
            num_questions=num_questions,
            agent_persona=agent_persona,
            agent_strictness=agent_strictness,
        )

        # Attach new fields
        interview.experience_level = experience_level
        interview.company_name = company_name
        interview.interview_mode = interview_mode
        interview.save(update_fields=["experience_level", "company_name", "interview_mode"])

        return Response(
            {"success": True, "interview": MockInterviewSerializer(interview).data},
            status=status.HTTP_201_CREATED,
        )

    interviews = MockInterview.objects.filter(user=user).order_by("-started_at")
    return Response({"success": True, "interviews": MockInterviewSerializer(interviews, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def interview_detail_view(request, pk):
    interview = get_object_or_404(MockInterview, pk=pk, user=request.user)
    MockInterviewService.ensure_chat_messages(interview)
    serializer_data = MockInterviewSerializer(interview).data
    current_q_data = serializer_data.get("current_question")
    return Response(
        {
            "success": True,
            "interview": serializer_data,
            "current_question": current_q_data,
            "messages": serializer_data.get("messages", []),
            "role": interview.target_role,
            "target_role": interview.target_role,
            "num_questions": interview.num_questions,
            "target_questions_count": interview.num_questions,
            "total_questions": interview.num_questions,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def interview_chat_view(request, pk):
    interview = get_object_or_404(MockInterview, pk=pk, user=request.user)
    raw_message = request.data.get("message") or request.data.get("content") or ""
    message = str(raw_message).strip()
    mode = request.data.get("mode") or request.data.get("type") or "chat"

    if not message:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Message is required."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = MockInterviewService.send_chat_message(interview, message=message, mode=mode)
    if "error" in result:
        return Response(
            {"success": False, "error": {"code": "CHAT_ERROR", "message": result["error"]}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"success": True, **result})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def interview_answer_view(request, pk):
    interview = get_object_or_404(MockInterview, pk=pk, user=request.user)
    raw_answer = request.data.get("answer") or request.data.get("content") or ""
    answer_text = str(raw_answer).strip()

    if not answer_text:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Answer text is required."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = MockInterviewService.submit_answer(interview, answer_text)
    if "error" in result:
        return Response(
            {"success": False, "error": {"code": "ANSWER_ERROR", "message": result["error"]}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"success": True, **result})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def interview_agent_interaction_view(request, pk):
    interview = get_object_or_404(MockInterview, pk=pk, user=request.user)
    interaction_type = request.data.get("type") or ("hint" if "hint" in request.path else "clarification")
    message = str(request.data.get("message") or "").strip()
    question_text = str(request.data.get("question_text") or "").strip()

    result = MockInterviewService.agent_interaction(
        interview=interview,
        interaction_type=interaction_type,
        message=message,
        question_text=question_text,
    )
    return Response({"success": True, **result})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def interview_finish_view(request, pk):
    interview = get_object_or_404(MockInterview, pk=pk, user=request.user)
    is_abandoned = request.data.get("abandoned", False)
    finished_interview = MockInterviewService.finish_interview(interview, is_abandoned=is_abandoned)
    result_data = MockInterviewService.get_result(finished_interview)
    return Response({"success": True, "result": result_data, "interview": MockInterviewSerializer(finished_interview).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def interview_result_view(request, pk):
    interview = get_object_or_404(MockInterview, pk=pk, user=request.user)
    result_data = MockInterviewService.get_result(interview)
    return Response({"success": True, "result": result_data})


# ==============================================================================
# SECTION 2: COMMUNICATION SECTION API VIEWS
# ==============================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def communication_topics_view(request):
    """Returns available communication practice modes, topics, and guide metadata."""
    return Response({
        "success": True,
        "modes": CommunicationService.MODES_METADATA,
        "topics_catalog": CommunicationService.TOPICS_CATALOG,
    })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def communication_list_create_view(request):
    user = request.user
    if request.method == "POST":
        mode = request.data.get("mode", "daily_practice")
        topic = request.data.get("topic", "")
        custom_scenario = request.data.get("scenario_prompt") or request.data.get("custom_scenario", "")

        session = CommunicationService.start_session(
            user=user,
            mode=mode,
            topic=topic,
            custom_scenario=custom_scenario,
        )
        return Response(
            {"success": True, "session": CommunicationSessionDetailSerializer(session).data},
            status=status.HTTP_201_CREATED,
        )

    sessions = CommunicationSession.objects.filter(user=user).order_by("-created_at")
    return Response({
        "success": True,
        "sessions": CommunicationSessionSerializer(sessions, many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def communication_detail_view(request, pk):
    session = get_object_or_404(CommunicationSession, pk=pk, user=request.user)
    return Response({
        "success": True,
        "session": CommunicationSessionDetailSerializer(session).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def communication_message_view(request, pk):
    session = get_object_or_404(CommunicationSession, pk=pk, user=request.user)
    message = request.data.get("message") or request.data.get("content") or ""
    audio_metrics = request.data.get("audio_metrics") or {}

    result = CommunicationService.process_turn(session, message, audio_metrics)
    if "error" in result:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": result["error"]}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def communication_finish_view(request, pk):
    session = get_object_or_404(CommunicationSession, pk=pk, user=request.user)
    completed_session = CommunicationService.finish_session(session)
    return Response({
        "success": True,
        "session": CommunicationSessionDetailSerializer(completed_session).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def audio_transcribe_view(request):
    """Transcribes user recorded audio into text using SpeechRecognition/ffmpeg or fallback."""
    import logging
    import os
    import subprocess
    import tempfile
    logger = logging.getLogger(__name__)

    audio_file = request.FILES.get("audio") or request.FILES.get("audio_file")
    context_hint = request.data.get("context", "")

    # Direct text pass-through if already transcribed
    if request.data.get("text"):
        return Response({"success": True, "transcript": request.data.get("text").strip()})

    transcript = ""

    # 1. Primary: Transcribe using SpeechRecognition + ffmpeg audio decoding
    if audio_file:
        try:
            import speech_recognition as sr
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

            with tempfile.TemporaryDirectory() as tmpdir:
                # Save uploaded file
                in_ext = ".webm" if "webm" in (audio_file.content_type or "") else ".wav"
                in_path = os.path.join(tmpdir, f"input{in_ext}")
                wav_path = os.path.join(tmpdir, "decoded.wav")

                with open(in_path, "wb") as f:
                    for chunk in audio_file.chunks():
                        f.write(chunk)

                # Convert to standard 16kHz mono PCM WAV
                conv = subprocess.run([
                    ffmpeg_exe, "-y", "-i", in_path,
                    "-ar", "16000", "-ac", "1", "-f", "wav", wav_path
                ], capture_output=True, timeout=15)

                if conv.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 100:
                    r = sr.Recognizer()
                    r.energy_threshold = 300
                    r.dynamic_energy_threshold = True
                    with sr.AudioFile(wav_path) as source:
                        audio_data = r.record(source)

                    try:
                        detected_text = r.recognize_google(audio_data, language="en-US")
                        if detected_text and len(detected_text.strip()) > 0:
                            transcript = detected_text.strip()
                    except sr.UnknownValueError:
                        # Audio was recorded but contained silence or inaudible whispering
                        logger.info("SpeechRecognition: No audible speech detected in recording.")
                    except sr.RequestError as req_err:
                        logger.warning(f"SpeechRecognition cloud service notice: {req_err}")
        except Exception as exc:
            logger.warning(f"Audio file decoding/recognition notice: {exc}")

    # 2. Secondary: If Gemini multimodal is configured and online
    if not transcript and audio_file:
        try:
            gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
            if gemini_key and not gemini_key.startswith("AQ."):
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                audio_file.seek(0)
                audio_bytes = audio_file.read()
                mime_type = audio_file.content_type or "audio/webm"
                audio_part = {"mime_type": mime_type, "data": audio_bytes}
                prompt = (
                    f"Transcribe the spoken words in this interview recording accurately. "
                    f"Context: {context_hint}. Output ONLY the transcribed words with zero additional commentary or tags."
                )
                response = model.generate_content([audio_part, prompt])
                if response and response.text:
                    transcript = response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini transcription notice: {e}")

    # 3. Explicit fallback if caller passed a fallback transcript
    if not transcript:
        fallback_text = request.data.get("fallback_text", "").strip()
        if fallback_text:
            transcript = fallback_text

    return Response({
        "success": True,
        "transcript": transcript,
        "has_audio": bool(audio_file),
    })


# ==============================================================================
# SECTION 3: SKILL ASSESSMENT API VIEWS
# ==============================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_problems_list_view(request):
    """List coding problems with difficulty, category, and search query filters."""
    problems = CodingProblem.objects.all().order_by("order", "id")

    difficulty = request.query_params.get("difficulty")
    if difficulty and difficulty != "all":
        problems = problems.filter(difficulty=difficulty.lower())

    category = request.query_params.get("category")
    if category and category != "all":
        problems = problems.filter(category=category.lower())

    search_query = request.query_params.get("search", "").strip()
    if search_query:
        problems = problems.filter(
            Q(title__icontains=search_query) | Q(category__icontains=search_query)
        )

    serializer = CodingProblemListSerializer(problems, many=True, context={"request": request})
    return Response({"success": True, "problems": serializer.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_problem_detail_view(request, slug):
    problem = get_object_or_404(CodingProblem, slug=slug)
    serializer = CodingProblemDetailSerializer(problem, context={"request": request})
    return Response({"success": True, "problem": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def skill_problem_run_code_view(request, slug):
    """Runs code against sample (public) test cases only."""
    problem = get_object_or_404(CodingProblem, slug=slug)
    code = request.data.get("code", "")
    language = request.data.get("language", "python")

    sample_cases = problem.test_cases.filter(is_hidden=False).order_by("order")
    if not sample_cases.exists():
        # Fallback to single run
        res = CodeExecutionService.execute_code(language, code, "", problem_slug=slug)
        return Response({"success": True, "results": [res], "all_passed": res["status"] == "Accepted"})

    results = []
    all_passed = True
    total_runtime = 0

    for tc in sample_cases:
        res = CodeExecutionService.execute_code(language, code, tc.input_data, problem_slug=slug)
        is_match = CodeExecutionService.test_case_matches(res["stdout"], tc.expected_output)
        status_label = "Accepted" if is_match and res["status"] == "Accepted" else (res["status"] if res["status"] != "Accepted" else "Wrong Answer")
        
        if status_label != "Accepted":
            all_passed = False

        total_runtime += res["runtime_ms"]
        results.append({
            "test_case_id": tc.id,
            "order": tc.order,
            "input": tc.input_data,
            "expected": tc.expected_output,
            "actual": res["stdout"],
            "stderr": res["stderr"],
            "status": status_label,
            "passed": status_label == "Accepted",
            "runtime_ms": res["runtime_ms"],
        })

    return Response({
        "success": True,
        "all_passed": all_passed,
        "average_runtime_ms": int(total_runtime / max(1, len(sample_cases))),
        "results": results,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def skill_problem_submit_code_view(request, slug):
    """Submits code against both sample AND hidden test cases, records submission."""
    problem = get_object_or_404(CodingProblem, slug=slug)
    code = request.data.get("code", "").strip()
    language = request.data.get("language", "python")

    if not code:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Code submission cannot be empty."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    all_test_cases = problem.test_cases.all().order_by("order")
    total_count = all_test_cases.count()
    passed_count = 0
    total_runtime = 0
    max_memory = 0
    overall_status = "Accepted"
    first_error = ""

    results_summary = []

    for tc in all_test_cases:
        res = CodeExecutionService.execute_code(language, code, tc.input_data, problem_slug=slug)
        is_match = CodeExecutionService.test_case_matches(res["stdout"], tc.expected_output)
        tc_status = "Accepted" if is_match and res["status"] == "Accepted" else (res["status"] if res["status"] != "Accepted" else "Wrong Answer")

        total_runtime += res["runtime_ms"]
        max_memory = max(max_memory, res["memory_kb"])

        if tc_status == "Accepted":
            passed_count += 1
        else:
            if overall_status == "Accepted":
                overall_status = tc_status
                first_error = res["stderr"] or res["error"] or f"Output mismatch on test case #{tc.order}"

        # If hidden, do not expose exact input/expected to client
        results_summary.append({
            "order": tc.order,
            "is_hidden": tc.is_hidden,
            "passed": tc_status == "Accepted",
            "status": tc_status,
            "runtime_ms": res["runtime_ms"],
            "input": tc.input_data if not tc.is_hidden else "[Hidden Test Case]",
            "expected": tc.expected_output if not tc.is_hidden else "[Hidden Test Case]",
            "actual": res["stdout"] if not tc.is_hidden else ("[Output Hidden]" if tc_status != "Accepted" else "[Matches Expected]"),
        })

    submission = CodingSubmission.objects.create(
        user=request.user,
        problem=problem,
        language=language,
        code=code,
        status=overall_status,
        runtime_ms=int(total_runtime / max(1, total_count)),
        memory_kb=max_memory,
        passed_test_cases=passed_count,
        total_test_cases=total_count,
        error_message=first_error,
        test_results=results_summary,
    )

    return Response({
        "success": True,
        "submission": CodingSubmissionSerializer(submission).data,
        "status": overall_status,
        "passed_test_cases": passed_count,
        "total_test_cases": total_count,
        "is_accepted": overall_status == "Accepted",
        "optimal_solutions": problem.optimal_solutions if overall_status == "Accepted" else None,
        "solution_explanation": problem.solution_explanation if overall_status == "Accepted" else None,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_quizzes_list_view(request):
    quizzes = TechnicalQuiz.objects.all().order_by("id")
    serializer = TechnicalQuizSerializer(quizzes, many=True, context={"request": request})
    return Response({"success": True, "quizzes": serializer.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_quiz_detail_view(request, slug):
    quiz = get_object_or_404(TechnicalQuiz, slug=slug)
    serializer = TechnicalQuizSerializer(quiz, context={"request": request})
    return Response({"success": True, "quiz": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def skill_quiz_submit_view(request, slug):
    quiz = get_object_or_404(TechnicalQuiz, slug=slug)
    user_answers = request.data.get("answers") or {}  # mapping: {"1": 0, "2": 1, ...}
    time_taken = int(request.data.get("time_taken_seconds", 0))

    questions = quiz.questions_data or []
    total_q = len(questions)
    correct_count = 0
    review_data = []

    for q in questions:
        q_id = str(q.get("id"))
        correct_idx = q.get("correct_index")
        chosen_idx = user_answers.get(q_id)
        is_correct = chosen_idx is not None and int(chosen_idx) == int(correct_idx)
        if is_correct:
            correct_count += 1
        review_data.append({
            "id": q.get("id"),
            "question": q.get("question"),
            "options": q.get("options", []),
            "chosen_index": chosen_idx,
            "correct_index": correct_idx,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score_pct = int((correct_count / max(1, total_q)) * 100)

    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        score=score_pct,
        total_correct=correct_count,
        total_questions=total_q,
        time_taken_seconds=time_taken,
        answers=user_answers,
        status="completed",
    )

    return Response({
        "success": True,
        "attempt": QuizAttemptSerializer(attempt).data,
        "score": score_pct,
        "total_correct": correct_count,
        "total_questions": total_q,
        "review": review_data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_analytics_view(request):
    """Calculates comprehensive coding analytics for the user."""
    user = request.user
    subs = CodingSubmission.objects.filter(user=user)
    
    # Problems solved
    accepted_subs = subs.filter(status="Accepted")
    solved_problem_ids = set(accepted_subs.values_list("problem_id", flat=True))
    total_solved = len(solved_problem_ids)

    # Breakdown by difficulty
    solved_problems = CodingProblem.objects.filter(id__in=solved_problem_ids)
    easy_solved = solved_problems.filter(difficulty="easy").count()
    medium_solved = solved_problems.filter(difficulty="medium").count()
    hard_solved = solved_problems.filter(difficulty="hard").count()

    total_easy = CodingProblem.objects.filter(difficulty="easy").count()
    total_medium = CodingProblem.objects.filter(difficulty="medium").count()
    total_hard = CodingProblem.objects.filter(difficulty="hard").count()

    # Accuracy percentage
    total_submissions = subs.count()
    accuracy_pct = int((accepted_subs.count() / max(1, total_submissions)) * 100) if total_submissions > 0 else 0

    # Average solving runtime
    avg_runtime = int(accepted_subs.aggregate(Avg("runtime_ms"))["runtime_ms__avg"] or 45)

    # Coding streak (consecutive active days)
    streak_days = _calculate_coding_streak(user)

    # Topic-wise performance
    categories = [
        "arrays", "strings", "linked_lists", "stacks_queues", "trees_graphs",
        "dynamic_programming", "searching_sorting", "recursion_backtracking", "sql", "problem_solving"
    ]
    topic_stats = []
    weak_topics = []

    for cat in categories:
        cat_total = CodingProblem.objects.filter(category=cat).count()
        cat_solved = solved_problems.filter(category=cat).count()
        cat_subs = subs.filter(problem__category=cat).count()
        mastery_pct = int((cat_solved / max(1, cat_total)) * 100) if cat_total > 0 else 0

        topic_stats.append({
            "category": cat,
            "label": cat.replace("_", " ").title(),
            "solved": cat_solved,
            "total": cat_total,
            "mastery_pct": mastery_pct,
            "submissions": cat_subs,
        })

        if cat_total > 0 and mastery_pct < 50:
            weak_topics.append({
                "category": cat,
                "label": cat.replace("_", " ").title(),
                "mastery_pct": mastery_pct,
                "recommendation": f"Practice {cat.replace('_', ' ').title()} core patterns to reach >70% mastery.",
            })

    # Recent submissions
    recent_submissions = CodingSubmissionSerializer(subs.order_by("-created_at")[:10], many=True).data

    return Response({
        "success": True,
        "analytics": {
            "total_solved": total_solved,
            "total_problems": CodingProblem.objects.count(),
            "accuracy_pct": accuracy_pct,
            "average_runtime_ms": avg_runtime,
            "streak_days": streak_days,
            "difficulty_breakdown": {
                "easy": {"solved": easy_solved, "total": total_easy},
                "medium": {"solved": medium_solved, "total": total_medium},
                "hard": {"solved": hard_solved, "total": total_hard},
            },
            "topic_performance": topic_stats,
            "weak_topics": weak_topics[:3],
            "recent_submissions": recent_submissions,
        }
    })


def _calculate_coding_streak(user) -> int:
    """Calculates consecutive active days with at least one submission."""
    dates = list(
        CodingSubmission.objects.filter(user=user)
        .dates("created_at", "day", order="DESC")
    )
    if not dates:
        return 0

    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)

    # Check if user submitted today or yesterday to maintain active streak
    if dates[0] not in (today, yesterday):
        return 0

    streak = 0
    current_check = dates[0]
    for d in dates:
        if d == current_check:
            streak += 1
            current_check = current_check - datetime.timedelta(days=1)
        else:
            break
    return streak


# ==============================================================================
# SECTION 4: INTERVIEWS HUB OVERVIEW STATS
# ==============================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def interviews_hub_stats_view(request):
    """Aggregated metrics across Job Interviews, Communication, and Skill Assessment."""
    user = request.user

    # 1. Job Interviews Stats
    user_interviews = MockInterview.objects.filter(user=user)
    completed_interviews = user_interviews.filter(status="completed")
    avg_interview_score = int(completed_interviews.aggregate(Avg("overall_score"))["overall_score__avg"] or 0)

    # 2. Communication Stats
    comm_sessions = CommunicationSession.objects.filter(user=user)
    completed_comm = comm_sessions.filter(status="completed")
    avg_comm_score = int(completed_comm.aggregate(Avg("overall_score"))["overall_score__avg"] or 0)
    avg_speed_wpm = int(completed_comm.aggregate(Avg("speed_wpm"))["speed_wpm__avg"] or 0)

    # 3. Skill Assessment Stats
    solved_count = len(set(
        CodingSubmission.objects.filter(user=user, status="Accepted").values_list("problem_id", flat=True)
    ))
    total_subs = CodingSubmission.objects.filter(user=user).count()
    accepted_subs = CodingSubmission.objects.filter(user=user, status="Accepted").count()
    coding_accuracy = int((accepted_subs / max(1, total_subs)) * 100) if total_subs > 0 else 0
    coding_streak = _calculate_coding_streak(user)

    return Response({
        "success": True,
        "hub": {
            "job_interviews": {
                "total_completed": completed_interviews.count(),
                "average_score": avg_interview_score,
                "target_role": user.target_role or "Software Developer",
                "recent_interviews": MockInterviewSerializer(user_interviews[:5], many=True).data,
            },
            "communication": {
                "total_sessions": completed_comm.count(),
                "average_score": avg_comm_score,
                "average_speed_wpm": avg_speed_wpm,
                "recent_sessions": CommunicationSessionSerializer(comm_sessions[:5], many=True).data,
            },
            "skill_assessment": {
                "problems_solved": solved_count,
                "accuracy_pct": coding_accuracy,
                "streak_days": coding_streak,
                "recent_submissions": CodingSubmissionSerializer(
                    CodingSubmission.objects.filter(user=user).order_by("-created_at")[:5], many=True
                ).data,
            },
        }
    })
