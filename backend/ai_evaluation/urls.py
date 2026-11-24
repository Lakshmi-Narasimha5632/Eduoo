from django.urls import path

from .views import ai_evaluation_view

urlpatterns = [
    path("", ai_evaluation_view, name="ai-evaluation"),
]
