"""Serializers for notifications and user preferences."""

from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "category",
            "is_read",
            "metadata",
            "email_sent",
            "email_sent_at",
            "email_recipient",
            "created_at",
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "email_notifications",
            "notification_email",
            "daily_task_reminders",
            "streak_reminders",
            "interview_reminders",
            "platform_sync_alerts",
            "weekly_summaries",
            "realtime_interview_email",
            "realtime_platform_sync_email",
            "realtime_task_email",
            "updated_at",
        ]
