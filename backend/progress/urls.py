from django.urls import path

from .views import progress_summary, weekly_progress

urlpatterns = [
    path("", progress_summary, name="progress-summary"),
    path("weekly/", weekly_progress, name="weekly-progress"),
]
