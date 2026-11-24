"""Notification domain services managing alerts and preference toggles."""

from __future__ import annotations

from typing import Any, Dict, List
from .email_service import EmailNotificationService
from .models import Notification, NotificationPreference


class NotificationService:
    @staticmethod
    def create_notification(
        user,
        title: str,
        message: str,
        category: str = "general",
        metadata: Dict[str, Any] | None = None,
        send_email: bool = True,
        action_url: str | None = None,
        action_label: str | None = None,
        extra_metrics: Dict[str, Any] | None = None,
    ) -> Notification | None:
        # Check preferences before creating
        prefs = NotificationService.get_or_create_preferences(user)
        if category == "task_reminder" and not prefs.daily_task_reminders:
            return None
        if category == "streak_reminder" and not prefs.streak_reminders:
            return None
        if category == "interview_reminder" and not prefs.interview_reminders:
            return None
        if category == "platform_sync" and not prefs.platform_sync_alerts:
            return None
        if category == "weekly_summary" and not prefs.weekly_summaries:
            return None

        notif = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            category=category,
            metadata=metadata or {},
        )

        # Dispatch real-time email if enabled
        if send_email:
            try:
                EmailNotificationService.dispatch_realtime_email(
                    notification=notif,
                    action_url=action_url,
                    action_label=action_label,
                    extra_metrics=extra_metrics,
                )
            except Exception:
                pass

        return notif

    @staticmethod
    def get_user_notifications(user, unread_only: bool = False) -> List[Notification]:
        qs = Notification.objects.filter(user=user)
        if unread_only:
            qs = qs.filter(is_read=False)
        return list(qs[:30])

    @staticmethod
    def mark_as_read(user, notification_id: int | None = None):
        if notification_id:
            Notification.objects.filter(user=user, id=notification_id).update(is_read=True)
        else:
            Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    @staticmethod
    def get_or_create_preferences(user) -> NotificationPreference:
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        return prefs

    @staticmethod
    def update_preferences(user, data: Dict[str, Any]) -> NotificationPreference:
        prefs = NotificationService.get_or_create_preferences(user)
        payload = data.get("preferences", data) if isinstance(data, dict) else {}

        field_mappings = {
            "email_notifications": "email_notifications",
            "notification_email": "notification_email",
            "daily_task_reminders": "daily_task_reminders",
            "daily_task_reminder": "daily_task_reminders",
            "streak_reminders": "streak_reminders",
            "interview_reminders": "interview_reminders",
            "platform_sync_alerts": "platform_sync_alerts",
            "weekly_summaries": "weekly_summaries",
            "weekly_progress_summary": "weekly_summaries",
            "realtime_interview_email": "realtime_interview_email",
            "realtime_platform_sync_email": "realtime_platform_sync_email",
            "realtime_task_email": "realtime_task_email",
        }

        for input_key, model_field in field_mappings.items():
            if input_key in payload:
                val = payload[input_key]
                if model_field == "notification_email":
                    setattr(prefs, model_field, str(val).strip() if val else None)
                else:
                    setattr(prefs, model_field, bool(val))

        prefs.save()
        return prefs

    @staticmethod
    def send_test_email(user, target_email: str | None = None) -> Dict[str, Any]:
        return EmailNotificationService.send_test_email(user=user, target_email=target_email)

    @staticmethod
    def send_registration_otp(recipient: str, otp_code: str, full_name: str | None = None, sync: bool = False) -> Dict[str, Any]:
        return EmailNotificationService.send_registration_otp_email(recipient=recipient, otp_code=otp_code, full_name=full_name, sync=sync)

    @staticmethod
    def send_task_completion_report(user, plan, extra_metrics: Dict[str, Any] | None = None, sync: bool = False) -> Dict[str, Any]:
        return EmailNotificationService.send_task_completion_report_email(user=user, plan=plan, extra_metrics=extra_metrics, sync=sync)

    @staticmethod
    def send_task_incomplete_alert(user, plan, extra_metrics: Dict[str, Any] | None = None, sync: bool = False) -> Dict[str, Any]:
        return EmailNotificationService.send_task_incomplete_alert_email(user=user, plan=plan, extra_metrics=extra_metrics, sync=sync)

