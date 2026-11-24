"""Notification URL routing."""

from django.urls import path
from .views import (
    notification_list_view,
    notification_mark_read_view,
    notification_preferences_view,
    notification_test_email_view,
)

urlpatterns = [
    path("", notification_list_view, name="notification-list"),
    path("read/", notification_mark_read_view, name="notification-read"),
    path("preferences/", notification_preferences_view, name="notification-preferences"),
    path("test-email/", notification_test_email_view, name="notification-test-email"),
]
