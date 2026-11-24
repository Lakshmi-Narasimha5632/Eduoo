"""Interviews URL routing for Job Interviews, Communication Practice, and Skill Assessment."""

from django.urls import path
from .views import (
    # Hub Overview
    interviews_hub_stats_view,
    audio_transcribe_view,
    # Section 1: Job Interviews
    interview_agent_interaction_view,
    interview_answer_view,
    interview_chat_view,
    interview_detail_view,
    interview_finish_view,
    interview_list_create_view,
    interview_result_view,
    # Section 2: Communication Practice
    communication_detail_view,
    communication_finish_view,
    communication_list_create_view,
    communication_message_view,
    communication_topics_view,
    # Section 3: Skill Assessment
    skill_analytics_view,
    skill_problem_detail_view,
    skill_problem_run_code_view,
    skill_problem_submit_code_view,
    skill_problems_list_view,
    skill_quiz_detail_view,
    skill_quiz_submit_view,
    skill_quizzes_list_view,
)

urlpatterns = [
    # Hub Overview Stats
    path("hub/stats/", interviews_hub_stats_view, name="interviews-hub-stats"),
    path("transcribe/", audio_transcribe_view, name="interviews-transcribe"),

    # Section 1: Job Interviews
    path("", interview_list_create_view, name="interview-list-create"),
    path("<int:pk>/", interview_detail_view, name="interview-detail"),
    path("<int:pk>/chat/", interview_chat_view, name="interview-chat"),
    path("<int:pk>/answer/", interview_answer_view, name="interview-answer"),
    path("<int:pk>/agent-interaction/", interview_agent_interaction_view, name="interview-agent-interaction"),
    path("<int:pk>/hint/", interview_agent_interaction_view, name="interview-hint"),
    path("<int:pk>/clarify/", interview_agent_interaction_view, name="interview-clarify"),
    path("<int:pk>/finish/", interview_finish_view, name="interview-finish"),
    path("<int:pk>/result/", interview_result_view, name="interview-result"),

    # Section 2: Communication Section
    path("communication/topics/", communication_topics_view, name="communication-topics"),
    path("communication/", communication_list_create_view, name="communication-list-create"),
    path("communication/<int:pk>/", communication_detail_view, name="communication-detail"),
    path("communication/<int:pk>/message/", communication_message_view, name="communication-message"),
    path("communication/<int:pk>/finish/", communication_finish_view, name="communication-finish"),

    # Section 3: Skill Assessment
    path("skills/problems/", skill_problems_list_view, name="skill-problems-list"),
    path("skills/problems/<slug:slug>/", skill_problem_detail_view, name="skill-problem-detail"),
    path("skills/problems/<slug:slug>/run/", skill_problem_run_code_view, name="skill-problem-run"),
    path("skills/problems/<slug:slug>/submit/", skill_problem_submit_code_view, name="skill-problem-submit"),
    path("skills/quizzes/", skill_quizzes_list_view, name="skill-quizzes-list"),
    path("skills/quizzes/<slug:slug>/", skill_quiz_detail_view, name="skill-quiz-detail"),
    path("skills/quizzes/<slug:slug>/submit/", skill_quiz_submit_view, name="skill-quiz-submit"),
    path("skills/analytics/", skill_analytics_view, name="skill-analytics"),
]
