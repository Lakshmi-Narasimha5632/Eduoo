"""Skills URL routing."""

from django.urls import path
from .views import (
    career_readiness_view,
    skill_gap_analysis_view,
    skill_list_view,
    user_skills_view,
)

urlpatterns = [
    path("", skill_list_view, name="skill-list"),
    path("my/", user_skills_view, name="user-skills"),
    path("gaps/", skill_gap_analysis_view, name="skill-gaps"),
    path("career-readiness/", career_readiness_view, name="career-readiness"),
]
