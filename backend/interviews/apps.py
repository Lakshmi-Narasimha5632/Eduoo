import os
import sys
from django.apps import AppConfig


class InterviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "interviews"

    def ready(self):
        # Auto-seed technical problems and quizzes when running server, not during migrations or pytest
        if "runserver" in sys.argv or "gunicorn" in sys.argv:
            try:
                from .seeds import seed_skill_assessments
                seed_skill_assessments()
            except Exception:
                pass
