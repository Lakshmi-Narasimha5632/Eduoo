"""Models for multi-turn AI mock interviews, dynamic questions, scored answers,
communication practice sessions, coding assessments, and technical challenges."""

from django.conf import settings
from django.db import models
from django.utils import timezone

from common.constants import INTERVIEW_DIFFICULTIES, INTERVIEW_TYPES


# ==============================================================================
# SECTION 1: JOB INTERVIEW MODELS
# ==============================================================================

class MockInterview(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    EXPERIENCE_CHOICES = [
        ("fresher", "Fresher (0-1 yrs)"),
        ("intermediate", "Intermediate (2-5 yrs)"),
        ("experienced", "Experienced (5+ yrs)"),
    ]

    CATEGORY_CHOICES = [
        ("technical", "Technical Interview"),
        ("hr", "HR Interview"),
        ("project_based", "Project-Based Interview"),
        ("company_specific", "Company-Specific Interview"),
        ("full_mock", "Full Mock Interview"),
        ("behavioral", "HR / Behavioral"),
        ("resume", "Resume-Based"),
        ("coding", "Coding & Algorithms"),
        ("system_design", "System Design"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mock_interviews")
    target_role = models.CharField(max_length=128)
    experience_level = models.CharField(max_length=32, choices=EXPERIENCE_CHOICES, default="intermediate")
    interview_type = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="technical")
    company_name = models.CharField(max_length=128, blank=True, default="")
    interview_mode = models.CharField(max_length=32, default="voice_text")  # text, voice, voice_text
    difficulty = models.CharField(max_length=32, choices=INTERVIEW_DIFFICULTIES, default="intermediate")
    duration_minutes = models.PositiveIntegerField(default=30)
    num_questions = models.PositiveSmallIntegerField(default=5)
    agent_persona = models.CharField(max_length=64, default="alex_architect", blank=True)
    agent_strictness = models.CharField(max_length=32, default="balanced", blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="in_progress")
    
    # Evaluation metrics
    overall_score = models.PositiveSmallIntegerField(null=True, blank=True)
    technical_score = models.PositiveSmallIntegerField(null=True, blank=True)
    communication_score = models.PositiveSmallIntegerField(null=True, blank=True)
    confidence_score = models.PositiveSmallIntegerField(null=True, blank=True)
    relevance_score = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, default="")
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    improvement_suggestions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    AGENT_PROFILES = {
        "alex_architect": {
            "id": "alex_architect",
            "name": "Alex Chen",
            "title": "Staff Systems Architect",
            "company": "Google",
            "pedigree": "Google / ex-Uber Staff",
            "style": "Rigorous System Architecture",
            "focus": "Distributed Systems, Scaling, Concurrency & High Throughput",
            "avatar_gradient": "from-cyan-500 to-blue-600",
            "voice_pitch": 1.0,
            "badge_color": "border-cyan-500/30 text-cyan-300 bg-cyan-500/10",
        },
        "sophia_algorithms": {
            "id": "sophia_algorithms",
            "name": "Dr. Sophia Lin",
            "title": "Principal Algorithm & AI Lead",
            "company": "DeepMind",
            "pedigree": "DeepMind / ex-Meta",
            "style": "Analytical & Invariant-Driven",
            "focus": "Data Structures, Asymptotic Optimality & Edge Cases",
            "avatar_gradient": "from-emerald-500 to-teal-600",
            "voice_pitch": 1.15,
            "badge_color": "border-emerald-500/30 text-emerald-300 bg-emerald-500/10",
        },
        "marcus_director": {
            "id": "marcus_director",
            "name": "Marcus Vance",
            "title": "VP of Engineering & Bar Raiser",
            "company": "Stripe",
            "pedigree": "Stripe / ex-Netflix",
            "style": "Strategic, STAR Behavioral & Impact",
            "focus": "Leadership Principles, System Tradeoffs & Team Ownership",
            "avatar_gradient": "from-amber-500 to-orange-600",
            "voice_pitch": 0.95,
            "badge_color": "border-amber-500/30 text-amber-300 bg-amber-500/10",
        },
        "elena_fullstack": {
            "id": "elena_fullstack",
            "name": "Elena Rostova",
            "title": "Principal Full Stack Architect",
            "company": "Vercel",
            "pedigree": "Vercel / ex-Airbnb",
            "style": "Pragmatic, UX & State Architecture",
            "focus": "Client Architecture, State Machines, APIs & Core Web Vitals",
            "avatar_gradient": "from-purple-500 to-pink-600",
            "voice_pitch": 1.1,
            "badge_color": "border-purple-500/30 text-purple-300 bg-purple-500/10",
        },
    }

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "-started_at"]),
            models.Index(fields=["status"]),
        ]

    @property
    def target_questions_count(self) -> int:
        return self.num_questions

    @property
    def agent_details(self) -> dict:
        persona = self.agent_persona or "alex_architect"
        return self.AGENT_PROFILES.get(persona, self.AGENT_PROFILES["alex_architect"])

    def __str__(self):
        return f"{self.user.email} - {self.target_role} ({self.interview_type}) [{self.status}]"


class InterviewQuestion(models.Model):
    interview = models.ForeignKey(MockInterview, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField()
    category = models.CharField(max_length=64, default="technical")
    difficulty = models.CharField(max_length=32, default="intermediate")
    order = models.PositiveSmallIntegerField(default=1)
    expected_answer = models.TextField(blank=True, null=True)
    is_follow_up = models.BooleanField(default=False)
    parent_question = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="follow_ups"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        unique_together = ("interview", "order")

    def __str__(self):
        return f"Q{self.order}: {self.question[:60]}..."


class InterviewAnswer(models.Model):
    question = models.OneToOneField(InterviewQuestion, on_delete=models.CASCADE, related_name="answer_record")
    answer = models.TextField()
    score = models.PositiveSmallIntegerField(default=75)
    technical_accuracy = models.PositiveSmallIntegerField(default=75)
    communication_score = models.PositiveSmallIntegerField(default=75)
    relevance_score = models.PositiveSmallIntegerField(default=75)
    confidence_score = models.PositiveSmallIntegerField(default=75)
    feedback = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    answered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["answered_at"]

    def __str__(self):
        return f"Answer for Q{self.question.order} (Score: {self.score})"


class InterviewChatMessage(models.Model):
    MESSAGE_TYPES = [
        ("greeting", "Greeting"),
        ("question", "Question"),
        ("answer", "Answer"),
        ("follow_up", "Follow Up"),
        ("hint", "Hint"),
        ("clarification", "Clarification"),
        ("feedback", "Feedback"),
        ("system", "System"),
    ]
    SENDER_CHOICES = [
        ("agent", "AI Interviewer"),
        ("candidate", "Candidate"),
        ("system", "System"),
    ]

    interview = models.ForeignKey(MockInterview, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.CharField(max_length=16, choices=SENDER_CHOICES, default="agent")
    message_type = models.CharField(max_length=32, choices=MESSAGE_TYPES, default="question")
    content = models.TextField()
    meta_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.interview_id}] {self.sender} ({self.message_type}): {self.content[:40]}"


# ==============================================================================
# SECTION 2: COMMUNICATION SECTION MODELS
# ==============================================================================

class CommunicationSession(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    MODE_CHOICES = [
        ("daily_practice", "Daily Communication Practice"),
        ("conversational", "AI Conversational Practice"),
        ("self_intro", "Self-Introduction Practice"),
        ("group_discussion", "Group Discussion Practice"),
        ("public_speaking", "Public Speaking Practice"),
        ("fluency_pronunciation", "Fluency & Pronunciation Exercises"),
        ("vocabulary", "Vocabulary Improvement"),
        ("grammar", "Grammar Correction"),
        ("sentence_formation", "Sentence Formation Practice"),
        ("workplace_scenarios", "Workplace Scenarios"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="communication_sessions")
    mode = models.CharField(max_length=64, choices=MODE_CHOICES, default="daily_practice")
    topic = models.CharField(max_length=256)
    scenario_prompt = models.TextField(blank=True, default="")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="in_progress")
    
    # Multi-dimensional AI Evaluation
    overall_score = models.PositiveSmallIntegerField(null=True, blank=True)
    pronunciation_score = models.PositiveSmallIntegerField(null=True, blank=True)
    grammar_score = models.PositiveSmallIntegerField(null=True, blank=True)
    fluency_score = models.PositiveSmallIntegerField(null=True, blank=True)
    vocabulary_score = models.PositiveSmallIntegerField(null=True, blank=True)
    speed_wpm = models.PositiveSmallIntegerField(null=True, blank=True)
    confidence_clarity_score = models.PositiveSmallIntegerField(null=True, blank=True)

    # Detailed feedback and improvement insights
    summary_feedback = models.TextField(blank=True, default="")
    mistakes_and_corrections = models.JSONField(default=list, blank=True)
    better_sentence_suggestions = models.JSONField(default=list, blank=True)
    areas_for_improvement = models.JSONField(default=list, blank=True)
    personalized_recommendations = models.JSONField(default=list, blank=True)

    total_words = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["mode"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.mode}: {self.topic[:30]} ({self.status})"


class CommunicationExchange(models.Model):
    session = models.ForeignKey(CommunicationSession, on_delete=models.CASCADE, related_name="exchanges")
    sender = models.CharField(max_length=32)  # 'user', 'ai_assistant', 'ai_peer_1', 'ai_peer_2', 'ai_moderator'
    sender_name = models.CharField(max_length=64, default="AI Coach")
    content = models.TextField()
    audio_metrics = models.JSONField(default=dict, blank=True)
    turn_feedback = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.session_id}] {self.sender_name}: {self.content[:40]}"


# ==============================================================================
# SECTION 3: SKILL ASSESSMENT SECTION MODELS
# ==============================================================================

class CodingProblem(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    CATEGORY_CHOICES = [
        ("arrays", "Arrays"),
        ("strings", "Strings"),
        ("linked_lists", "Linked Lists"),
        ("stacks_queues", "Stacks and Queues"),
        ("trees_graphs", "Trees and Graphs"),
        ("dynamic_programming", "Dynamic Programming"),
        ("searching_sorting", "Searching and Sorting"),
        ("recursion_backtracking", "Recursion and Backtracking"),
        ("sql", "SQL"),
        ("problem_solving", "Problem Solving"),
    ]

    slug = models.SlugField(max_length=128, unique=True)
    title = models.CharField(max_length=256)
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES, default="easy")
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default="arrays")
    description = models.TextField()
    input_format = models.TextField(blank=True, default="")
    output_format = models.TextField(blank=True, default="")
    constraints = models.TextField(blank=True, default="")
    starter_templates = models.JSONField(default=dict, blank=True)
    solution_explanation = models.TextField(blank=True, default="")
    optimal_solutions = models.JSONField(default=dict, blank=True)
    hints = models.JSONField(default=list, blank=True)
    acceptance_rate = models.FloatField(default=72.5)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["difficulty"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"[{self.difficulty.upper()}] {self.title} ({self.category})"


class ProblemTestCase(models.Model):
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name="test_cases")
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, default="")
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        kind = "Hidden" if self.is_hidden else "Sample"
        return f"{self.problem.title} - TC #{self.order} ({kind})"


class CodingSubmission(models.Model):
    STATUS_CHOICES = [
        ("Accepted", "Accepted"),
        ("Wrong Answer", "Wrong Answer"),
        ("Time Limit Exceeded", "Time Limit Exceeded"),
        ("Runtime Error", "Runtime Error"),
        ("Compilation Error", "Compilation Error"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coding_submissions")
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name="submissions")
    language = models.CharField(max_length=32, default="python")
    code = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="Accepted")
    runtime_ms = models.PositiveIntegerField(default=0)
    memory_kb = models.PositiveIntegerField(default=0)
    passed_test_cases = models.PositiveIntegerField(default=0)
    total_test_cases = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    test_results = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["problem", "status"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.problem.title} [{self.language}]: {self.status}"


class TechnicalQuiz(models.Model):
    CATEGORY_CHOICES = [
        ("python", "Python Programming"),
        ("javascript", "JavaScript & Web"),
        ("sql", "SQL & Relational Databases"),
        ("dsa", "Data Structures & Algorithms"),
        ("technical_mcq", "Technical Core (OS, Networks, Design)"),
        ("aptitude", "Aptitude & Logical Reasoning"),
    ]

    slug = models.SlugField(max_length=128, unique=True)
    title = models.CharField(max_length=256)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default="python")
    description = models.TextField(blank=True, default="")
    time_limit_minutes = models.PositiveSmallIntegerField(default=20)
    total_questions = models.PositiveSmallIntegerField(default=10)
    questions_data = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.title} ({self.category})"


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(TechnicalQuiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveSmallIntegerField(default=0)  # Percentage 0-100
    total_correct = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    answers = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, default="completed")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]
        indexes = [
            models.Index(fields=["user", "-completed_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} ({self.score}%)"
