"""Serializers for multi-turn mock interviews, dynamic questions, scored answers,
communication practice sessions, coding assessments, and technical challenges."""

from rest_framework import serializers
from .models import (
    CodingProblem,
    CodingSubmission,
    CommunicationExchange,
    CommunicationSession,
    InterviewAnswer,
    InterviewChatMessage,
    InterviewQuestion,
    MockInterview,
    ProblemTestCase,
    QuizAttempt,
    TechnicalQuiz,
)


# ==============================================================================
# SECTION 1: JOB INTERVIEWS SERIALIZERS
# ==============================================================================

class InterviewChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewChatMessage
        fields = [
            "id",
            "sender",
            "message_type",
            "content",
            "meta_info",
            "created_at",
        ]


class InterviewAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewAnswer
        fields = [
            "id",
            "answer",
            "score",
            "technical_accuracy",
            "communication_score",
            "relevance_score",
            "confidence_score",
            "feedback",
            "strengths",
            "weaknesses",
            "suggestions",
            "answered_at",
        ]


class InterviewQuestionSerializer(serializers.ModelSerializer):
    answer = InterviewAnswerSerializer(source="answer_record", read_only=True)
    question_text = serializers.CharField(source="question", read_only=True)

    class Meta:
        model = InterviewQuestion
        fields = [
            "id",
            "question",
            "question_text",
            "category",
            "difficulty",
            "order",
            "is_follow_up",
            "answer",
        ]


class MockInterviewSerializer(serializers.ModelSerializer):
    questions = InterviewQuestionSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    current_question = serializers.SerializerMethodField()
    role = serializers.CharField(source="target_role", read_only=True)
    target_questions_count = serializers.IntegerField(source="num_questions", read_only=True)
    agent_details = serializers.ReadOnlyField()
    questions_count = serializers.SerializerMethodField()
    answered_count = serializers.SerializerMethodField()
    is_empty = serializers.SerializerMethodField()

    class Meta:
        model = MockInterview
        fields = [
            "id",
            "target_role",
            "role",
            "experience_level",
            "interview_type",
            "company_name",
            "interview_mode",
            "difficulty",
            "duration_minutes",
            "num_questions",
            "target_questions_count",
            "agent_persona",
            "agent_strictness",
            "agent_details",
            "started_at",
            "completed_at",
            "status",
            "overall_score",
            "technical_score",
            "communication_score",
            "confidence_score",
            "relevance_score",
            "feedback",
            "strengths",
            "weaknesses",
            "improvement_suggestions",
            "questions",
            "messages",
            "current_question",
            "questions_count",
            "answered_count",
            "is_empty",
        ]

    def get_messages(self, obj):
        return InterviewChatMessageSerializer(obj.chat_messages.all(), many=True).data

    def get_current_question(self, obj):
        current_q = obj.questions.filter(answer_record__isnull=True).order_by("order").first()
        if not current_q and obj.questions.exists():
            current_q = obj.questions.order_by("-order").first()
        if current_q:
            return InterviewQuestionSerializer(current_q).data
        return None

    def get_questions_count(self, obj):
        return obj.questions.count()

    def get_answered_count(self, obj):
        return obj.questions.filter(answer_record__isnull=False).count()

    def get_is_empty(self, obj):
        return obj.questions.filter(answer_record__isnull=False).count() == 0


# ==============================================================================
# SECTION 2: COMMUNICATION SECTION SERIALIZERS
# ==============================================================================

class CommunicationExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationExchange
        fields = [
            "id",
            "sender",
            "sender_name",
            "content",
            "audio_metrics",
            "turn_feedback",
            "created_at",
        ]


class CommunicationSessionSerializer(serializers.ModelSerializer):
    exchanges_count = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationSession
        fields = [
            "id",
            "mode",
            "topic",
            "scenario_prompt",
            "status",
            "overall_score",
            "pronunciation_score",
            "grammar_score",
            "fluency_score",
            "vocabulary_score",
            "speed_wpm",
            "confidence_clarity_score",
            "total_words",
            "duration_seconds",
            "created_at",
            "completed_at",
            "exchanges_count",
        ]

    def get_exchanges_count(self, obj):
        return obj.exchanges.count()


class CommunicationSessionDetailSerializer(serializers.ModelSerializer):
    exchanges = CommunicationExchangeSerializer(many=True, read_only=True)

    class Meta:
        model = CommunicationSession
        fields = [
            "id",
            "mode",
            "topic",
            "scenario_prompt",
            "status",
            "overall_score",
            "pronunciation_score",
            "grammar_score",
            "fluency_score",
            "vocabulary_score",
            "speed_wpm",
            "confidence_clarity_score",
            "summary_feedback",
            "mistakes_and_corrections",
            "better_sentence_suggestions",
            "areas_for_improvement",
            "personalized_recommendations",
            "total_words",
            "duration_seconds",
            "created_at",
            "completed_at",
            "exchanges",
        ]


# ==============================================================================
# SECTION 3: SKILL ASSESSMENT SERIALIZERS
# ==============================================================================

class ProblemTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTestCase
        fields = [
            "id",
            "input_data",
            "expected_output",
            "is_hidden",
            "explanation",
            "order",
        ]


class CodingProblemListSerializer(serializers.ModelSerializer):
    user_status = serializers.SerializerMethodField()
    test_cases_count = serializers.SerializerMethodField()

    class Meta:
        model = CodingProblem
        fields = [
            "id",
            "slug",
            "title",
            "difficulty",
            "category",
            "acceptance_rate",
            "order",
            "user_status",
            "test_cases_count",
        ]

    def get_user_status(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            last_sub = obj.submissions.filter(user=request.user).order_by("-created_at").first()
            if last_sub:
                return "Solved" if last_sub.status == "Accepted" else "Attempted"
        return "Unsolved"

    def get_test_cases_count(self, obj):
        return obj.test_cases.count()


class CodingProblemDetailSerializer(serializers.ModelSerializer):
    sample_test_cases = serializers.SerializerMethodField()
    user_submissions = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = CodingProblem
        fields = [
            "id",
            "slug",
            "title",
            "difficulty",
            "category",
            "acceptance_rate",
            "description",
            "input_format",
            "output_format",
            "constraints",
            "starter_templates",
            "hints",
            "sample_test_cases",
            "solution_explanation",
            "optimal_solutions",
            "user_submissions",
            "user_status",
        ]

    def get_sample_test_cases(self, obj):
        samples = obj.test_cases.filter(is_hidden=False).order_by("order")
        return ProblemTestCaseSerializer(samples, many=True).data

    def get_user_submissions(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            subs = obj.submissions.filter(user=request.user).order_by("-created_at")[:10]
            return CodingSubmissionSerializer(subs, many=True).data
        return []

    def get_user_status(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            solved = obj.submissions.filter(user=request.user, status="Accepted").exists()
            if solved:
                return "Solved"
            if obj.submissions.filter(user=request.user).exists():
                return "Attempted"
        return "Unsolved"


class CodingSubmissionSerializer(serializers.ModelSerializer):
    problem_title = serializers.CharField(source="problem.title", read_only=True)
    problem_slug = serializers.CharField(source="problem.slug", read_only=True)
    problem_difficulty = serializers.CharField(source="problem.difficulty", read_only=True)

    class Meta:
        model = CodingSubmission
        fields = [
            "id",
            "problem_title",
            "problem_slug",
            "problem_difficulty",
            "language",
            "code",
            "status",
            "runtime_ms",
            "memory_kb",
            "passed_test_cases",
            "total_test_cases",
            "error_message",
            "test_results",
            "created_at",
        ]


class TechnicalQuizSerializer(serializers.ModelSerializer):
    user_highest_score = serializers.SerializerMethodField()
    total_attempts = serializers.SerializerMethodField()

    class Meta:
        model = TechnicalQuiz
        fields = [
            "id",
            "slug",
            "title",
            "category",
            "description",
            "time_limit_minutes",
            "total_questions",
            "questions_data",
            "user_highest_score",
            "total_attempts",
        ]

    def get_user_highest_score(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            att = obj.attempts.filter(user=request.user).order_by("-score").first()
            return att.score if att else None
        return None

    def get_total_attempts(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.attempts.filter(user=request.user).count()
        return 0


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    quiz_slug = serializers.CharField(source="quiz.slug", read_only=True)
    quiz_category = serializers.CharField(source="quiz.category", read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz_title",
            "quiz_slug",
            "quiz_category",
            "score",
            "total_correct",
            "total_questions",
            "time_taken_seconds",
            "answers",
            "status",
            "completed_at",
        ]
