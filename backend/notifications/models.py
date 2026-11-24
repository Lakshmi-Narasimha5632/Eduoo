"""Notification and user preference models."""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    CATEGORY_CHOICES = [
        ("task_reminder", "Daily Task Reminder"),
        ("streak_reminder", "Streak Alert"),
        ("interview_reminder", "Interview Reminder"),
        ("platform_sync", "Platform Sync Status"),
        ("weekly_summary", "Weekly Progress Summary"),
        ("general", "General Notification"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="general")
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_recipient = models.EmailField(max_length=255, null=True, blank=True)
    email_error = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title} [{'Read' if self.is_read else 'Unread'}]"


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
    email_notifications = models.BooleanField(default=True)
    notification_email = models.EmailField(max_length=255, blank=True, null=True)
    daily_task_reminders = models.BooleanField(default=True)
    streak_reminders = models.BooleanField(default=True)
    interview_reminders = models.BooleanField(default=True)
    platform_sync_alerts = models.BooleanField(default=True)
    weekly_summaries = models.BooleanField(default=True)
    realtime_interview_email = models.BooleanField(default=True)
    realtime_platform_sync_email = models.BooleanField(default=True)
    realtime_task_email = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"
