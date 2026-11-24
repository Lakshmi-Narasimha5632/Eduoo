"""Resume URL routing."""

from django.urls import path
from .views import (
    resume_analyze_view,
    resume_edit_parsed_view,
    resume_overview,
    resume_upload_view,
)

urlpatterns = [
    path("", resume_overview, name="resume-overview"),
    path("upload/", resume_upload_view, name="resume-upload"),
    path("analyze/", resume_analyze_view, name="resume-analyze"),
    path("parsed/", resume_edit_parsed_view, name="resume-edit-parsed"),
]
