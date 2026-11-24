from django.urls import path

from .views import mock_interviews_view

urlpatterns = [
    path("", mock_interviews_view, name="mock-interviews"),
]
