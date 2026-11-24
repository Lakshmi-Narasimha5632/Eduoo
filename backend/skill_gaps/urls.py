from django.urls import path

from .views import skill_gaps_view

urlpatterns = [
    path("", skill_gaps_view, name="skill-gaps-list"),
]
