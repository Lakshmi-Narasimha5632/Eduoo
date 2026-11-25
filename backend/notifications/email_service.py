"""Real-time email notification service with rich HTML templates and non-blocking asynchronous dispatch."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import escape

logger = logging.getLogger(__name__)

# Non-blocking executor for immediate asynchronous dispatch without blocking user HTTP requests
_email_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="eduoo_email_worker")


class EmailNotificationService:
    @staticmethod
    def get_recipient_email(user, prefs=None) -> Optional[str]:
        if prefs and prefs.notification_email and prefs.notification_email.strip():
            return prefs.notification_email.strip()
        if user and hasattr(user, "email") and user.email and user.email.strip():
            return user.email.strip()
        return None

    @classmethod
    def should_send_email(cls, user, category: str, prefs=None) -> bool:
        if not prefs:
            from .models import NotificationPreference
            prefs, _ = NotificationPreference.objects.get_or_create(user=user)

        if not prefs.email_notifications:
            return False

        if category == "interview_reminder" and not prefs.realtime_interview_email:
            return False
        if category == "platform_sync" and not prefs.realtime_platform_sync_email:
            return False
        if category in ("task_reminder", "streak_reminder") and not prefs.realtime_task_email:
            return False

        return True

    @classmethod
    def dispatch_realtime_email(
        cls,
        notification,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        extra_metrics: Optional[Dict[str, Any]] = None,
    ):
        """Asynchronously dispatches a real-time email for a Notification instance."""
        user = notification.user
        from .models import NotificationPreference
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)

        if not cls.should_send_email(user, notification.category, prefs):
            return

        recipient = cls.get_recipient_email(user, prefs)
        if not recipient:
            logger.info("Skipping real-time email: no recipient email found for user %s", user)
            return

        # Prepare payload and queue execution in thread pool
        notification_id = notification.id
        title = notification.title
        message = notification.message
        category = notification.category
        metadata = notification.metadata or {}
        combined_metrics = {**metadata.get("metrics", {}), **(extra_metrics or {})}

        _email_executor.submit(
            cls._send_email_task,
            notification_id=notification_id,
            recipient=recipient,
            title=title,
            message=message,
            category=category,
            action_url=action_url,
            action_label=action_label,
            metrics=combined_metrics,
        )

    @classmethod
    def send_test_email(cls, user, target_email: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches an immediate real-time test email to verify SMTP / email pipeline."""
        from .models import Notification, NotificationPreference

        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        recipient = (target_email or "").strip() or cls.get_recipient_email(user, prefs)
        if not recipient:
            raise ValueError("No recipient email address configured.")

        notif = Notification.objects.create(
            user=user,
            title="Eduoo Real-Time Email Notifications Verified! 🚀",
            message=(
                "Your real-time notification pipeline is active and working. You will receive "
                "instant email updates whenever you complete mock interviews, sync platforms, "
                "or hit daily study milestones."
            ),
            category="general",
            metadata={
                "is_test": True,
                "verified_at": timezone.now().isoformat(),
            },
        )

        # Synchronous test send to give immediate HTTP feedback
        result = cls._send_email_task(
            notification_id=notif.id,
            recipient=recipient,
            title=notif.title,
            message=notif.message,
            category=notif.category,
            action_url="http://localhost:5173/profile",
            action_label="Manage Preferences in Profile",
            metrics={
                "Engine Status": "Active & Connected",
                "Recipient": recipient,
                "Delivery Mode": "Real-Time Push",
                "Environment": "Production Ready" if not settings.DEBUG else "Local Development",
            },
            sync=True,
        )

        return {
            "success": result.get("success", False),
            "recipient": recipient,
            "notification_id": notif.id,
            "message": result.get("message", "Test email dispatched successfully!"),
            "error": result.get("error"),
        }

    @classmethod
    def _send_custom_html_email(
        cls,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches an email with custom HTML & plain text bodies."""
        def _task():
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Eduoo AI <notifications@eduoo.ai>")
            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=from_email,
                    to=[recipient],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                logger.info("Successfully delivered custom email '%s' to %s", subject, recipient)
                return {"success": True, "recipient": recipient, "message": "Email delivered successfully"}
            except Exception as exc:
                raw_error = str(exc)
                if "534" in raw_error or "WebLoginRequired" in raw_error:
                    error_msg = (
                        "Google rejected the login (534 WebLoginRequired / App Password required). "
                        "Please ensure: 1) 2-Step Verification is turned ON for this Google account, "
                        "2) The 16-letter App Password was generated while logged into this exact Gmail account at https://myaccount.google.com/apppasswords, "
                        "and 3) Unlock SMTP access at https://accounts.google.com/DisplayUnlockCaptcha while logged into this account."
                    )
                elif "535" in raw_error or "BadCredentials" in raw_error:
                    error_msg = (
                        "Google rejected the credentials (535 BadCredentials). "
                        "Please verify the 16-letter App Password in .env was copied correctly."
                    )
                else:
                    error_msg = raw_error

                # Prominently print in terminal console so local developers/users see OTPs/reports immediately
                try:
                    print("\n" + "=" * 70, flush=True)
                    print("[WARNING] [EDUOO EMAIL SMTP DELIVERY FAILED]", flush=True)
                    print(f"Recipient: {recipient}", flush=True)
                    print(f"Subject:   {subject}", flush=True)
                    print(f"Reason:    {error_msg}", flush=True)
                    print("-" * 70, flush=True)
                    print(f"CONSOLE EMAIL CONTENT FALLBACK:\n{text_body}", flush=True)
                    print("=" * 70 + "\n", flush=True)
                except Exception:
                    pass

                logger.error("Failed to deliver custom email '%s' to %s: %s", subject, recipient, error_msg)
                return {"success": False, "recipient": recipient, "error": error_msg}

        if sync:
            return _task()
        _email_executor.submit(_task)
        return {"success": True, "recipient": recipient, "message": "Email queued for dispatch"}

    @classmethod
    def send_registration_otp_email(
        cls,
        recipient: str,
        otp_code: str,
        full_name: Optional[str] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Sends a 6-digit OTP verification code to a new user upon registration."""
        subject = "[Eduoo AI] Verify Your Email - OTP Verification Code"
        greeting = f"Hello {escape(full_name)}," if full_name else "Welcome to Eduoo AI,"

        html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Verification Code</title>
</head>
<body style="margin: 0; padding: 0; background-color: #090d16; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
    <div style="max-width: 580px; margin: 30px auto; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
        <div style="height: 4px; background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);"></div>
        <div style="padding: 24px 28px 16px 28px; border-bottom: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-size: 20px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff;">Eduoo<span style="color: #6366f1;">.AI</span></span>
                <span style="display: block; font-size: 11px; color: #64748b; font-weight: 500;">Account Verification</span>
            </div>
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 700; color: #818cf8;">
                🔒 Email Verification
            </div>
        </div>
        <div style="padding: 28px;">
            <p style="font-size: 15px; color: #cbd5e1; margin-top: 0;">{greeting}</p>
            <p style="font-size: 14px; color: #94a3b8; line-height: 1.6;">
                Thank you for joining Eduoo! To complete your registration and activate your personalized AI learning roadmap, please enter the 6-digit verification code below:
            </p>
            
            <div style="margin: 30px 0; text-align: center;">
                <div style="display: inline-block; background: #1e293b; border: 2px dashed #6366f1; border-radius: 12px; padding: 18px 36px; font-size: 34px; font-weight: 900; letter-spacing: 12px; color: #a5b4fc; font-family: monospace;">
                    {escape(otp_code)}
                </div>
            </div>

            <div style="background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.2); border-radius: 8px; padding: 12px 16px; margin: 20px 0; font-size: 12px; color: #fda4af;">
                ⚠️ <strong>Security Notice:</strong> This OTP is valid for <strong>10 minutes</strong>. Do not share this code with anyone. Eduoo staff will never ask for your verification code.
            </div>
        </div>
        <div style="padding: 18px 28px; background-color: #0a0f1d; border-top: 1px solid #1e293b; font-size: 11px; color: #64748b; text-align: center; line-height: 1.5;">
            If you did not initiate this registration, please disregard this email.<br/>
            &copy; Eduoo AI Learning Platform. All rights reserved.
        </div>
    </div>
</body>
</html>
"""

        text_body = f"""[Eduoo AI] Email Verification Code
====================================

{greeting}

Your 6-digit email verification OTP is:
{otp_code}

This code is valid for 10 minutes. Please enter it on the registration screen to activate your account.
If you did not request this, please disregard this email.
"""

        return cls._send_custom_html_email(recipient=recipient, subject=subject, html_body=html_body, text_body=text_body, sync=sync)

    @classmethod
    def send_task_completion_report_email(
        cls,
        user,
        plan,
        extra_metrics: Optional[Dict[str, Any]] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches an automated Daily Task Completion Report to the user's verified email."""
        recipient = (user.email or "").strip()
        if not recipient:
            return {"success": False, "error": "User does not have an email address."}

        plan_date_str = str(plan.date)
        subject = f"[Eduoo AI] Daily Study Report: All Tasks Completed! 🌟 ({plan_date_str})"
        tasks = list(plan.tasks.all())
        total_tasks = len(tasks)
        completed_tasks = [t for t in tasks if t.status == "completed"]
        total_mins = plan.completed_minutes or sum(t.estimated_minutes for t in completed_tasks)

        # Build task table rows
        task_rows = ""
        text_task_lines = []
        for t in tasks:
            status_icon = "✔️" if t.status == "completed" else "⏳"
            task_rows += f"""
            <tr style="border-bottom: 1px solid #1e293b;">
                <td style="padding: 12px 14px; font-size: 13px; font-weight: 600; color: #f8fafc;">
                    {escape(t.title)}
                    <span style="display: block; font-size: 11px; color: #94a3b8; font-weight: 400; margin-top: 2px;">{escape(t.topic or t.task_type)}</span>
                </td>
                <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1; text-align: center;">
                    <span style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; padding: 2px 8px; border-radius: 12px; font-size: 11px;">
                        {escape(t.task_type.capitalize())}
                    </span>
                </td>
                <td style="padding: 12px 14px; font-size: 12px; color: #38bdf8; text-align: center; font-weight: 600;">
                    {t.estimated_minutes} min
                </td>
                <td style="padding: 12px 14px; font-size: 12px; color: #34d399; text-align: right; font-weight: 700;">
                    {status_icon} Completed
                </td>
            </tr>
            """
            text_task_lines.append(f" - [COMPLETED] {t.title} ({t.estimated_minutes} min, {t.topic})")

        html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Study Report</title>
</head>
<body style="margin: 0; padding: 0; background-color: #090d16; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
    <div style="max-width: 600px; margin: 30px auto; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
        <div style="height: 4px; background: linear-gradient(90deg, #10b981, #6366f1, #38bdf8);"></div>
        <div style="padding: 24px 28px 16px 28px; border-bottom: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-size: 20px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff;">Eduoo<span style="color: #10b981;">.AI</span></span>
                <span style="display: block; font-size: 11px; color: #64748b; font-weight: 500;">Daily Study Report</span>
            </div>
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 700; color: #34d399;">
                🌟 100% Completed
            </div>
        </div>
        <div style="padding: 28px;">
            <h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 800; color: #ffffff;">
                Outstanding Job, {escape(user.full_name or user.username)}! 🎉
            </h2>
            <p style="font-size: 14px; color: #94a3b8; line-height: 1.6; margin-top: 0;">
                You have successfully completed all scheduled learning and practice tasks for <strong>{escape(plan_date_str)}</strong>. Here is your daily completion report:
            </p>

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0;">
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Tasks Finished</div>
                    <div style="font-size: 18px; font-weight: 800; color: #34d399; margin-top: 4px;">{len(completed_tasks)} / {total_tasks}</div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Study Time</div>
                    <div style="font-size: 18px; font-weight: 800; color: #38bdf8; margin-top: 4px;">{total_mins} min</div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Target Role</div>
                    <div style="font-size: 13px; font-weight: 700; color: #e2e8f0; margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {escape(user.target_role or 'Developer')}
                    </div>
                </div>
            </div>

            <h3 style="font-size: 14px; font-weight: 700; color: #cbd5e1; margin: 24px 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Completed Tasks Breakdown
            </h3>
            <table style="width: 100%; border-collapse: collapse; background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #1e293b; color: #94a3b8; font-size: 11px; text-transform: uppercase; text-align: left;">
                        <th style="padding: 10px 14px;">Task</th>
                        <th style="padding: 10px 14px; text-align: center;">Type</th>
                        <th style="padding: 10px 14px; text-align: center;">Time</th>
                        <th style="padding: 10px 14px; text-align: right;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {task_rows}
                </tbody>
            </table>

            <div style="margin: 28px 0 10px 0; text-align: center;">
                <a href="http://localhost:5173/daily-tasks" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-size: 14px; font-weight: 700; display: inline-block; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);">
                    View Tomorrow's Tasks on Eduoo &rarr;
                </a>
            </div>
        </div>
        <div style="padding: 18px 28px; background-color: #0a0f1d; border-top: 1px solid #1e293b; font-size: 11px; color: #64748b; text-align: center; line-height: 1.5;">
            This automated daily report was delivered to your verified email: {escape(recipient)}.<br/>
            &copy; Eduoo AI Learning Platform.
        </div>
    </div>
</body>
</html>
"""

        text_body = f"""[Eduoo AI] Daily Study Report - All Tasks Completed!
===================================================

Congratulations {user.full_name or user.username}!
You completed all {len(completed_tasks)} tasks for {plan_date_str}, logging {total_mins} minutes of focused learning.

Tasks Completed:
{chr(10).join(text_task_lines)}

View your progress and tomorrow's plan at: http://localhost:5173/daily-tasks
"""

        return cls._send_custom_html_email(recipient=recipient, subject=subject, html_body=html_body, text_body=text_body, sync=sync)

    @classmethod
    def send_task_incomplete_alert_email(
        cls,
        user,
        plan,
        extra_metrics: Optional[Dict[str, Any]] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches an automated alert email when daily tasks are not completed to the verified email."""
        recipient = (user.email or "").strip()
        if not recipient:
            return {"success": False, "error": "User does not have an email address."}

        plan_date_str = str(plan.date)
        subject = f"[Eduoo AI] Daily Study Alert: You have pending tasks remaining today! ⚠️ ({plan_date_str})"
        tasks = list(plan.tasks.all())
        pending_tasks = [t for t in tasks if t.status != "completed"]
        completed_tasks = [t for t in tasks if t.status == "completed"]
        remaining_mins = sum(t.estimated_minutes for t in pending_tasks)

        # Build pending task table rows
        task_rows = ""
        text_task_lines = []
        for t in pending_tasks:
            task_rows += f"""
            <tr style="border-bottom: 1px solid #1e293b;">
                <td style="padding: 12px 14px; font-size: 13px; font-weight: 600; color: #f8fafc;">
                    {escape(t.title)}
                    <span style="display: block; font-size: 11px; color: #94a3b8; font-weight: 400; margin-top: 2px;">{escape(t.topic or t.task_type)}</span>
                </td>
                <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1; text-align: center;">
                    <span style="background: rgba(245, 158, 11, 0.15); color: #fcd34d; padding: 2px 8px; border-radius: 12px; font-size: 11px;">
                        {escape(t.task_type.capitalize())}
                    </span>
                </td>
                <td style="padding: 12px 14px; font-size: 12px; color: #38bdf8; text-align: center; font-weight: 600;">
                    {t.estimated_minutes} min
                </td>
                <td style="padding: 12px 14px; font-size: 12px; color: #f59e0b; text-align: right; font-weight: 700;">
                    ⏳ Pending
                </td>
            </tr>
            """
            text_task_lines.append(f" - [PENDING] {t.title} ({t.estimated_minutes} min, {t.topic})")

        html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Study Alert - Incomplete Tasks</title>
</head>
<body style="margin: 0; padding: 0; background-color: #090d16; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
    <div style="max-width: 600px; margin: 30px auto; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
        <div style="height: 4px; background: linear-gradient(90deg, #f59e0b, #ef4444, #ec4899);"></div>
        <div style="padding: 24px 28px 16px 28px; border-bottom: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-size: 20px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff;">Eduoo<span style="color: #f59e0b;">.AI</span></span>
                <span style="display: block; font-size: 11px; color: #64748b; font-weight: 500;">Daily Study Alert</span>
            </div>
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 700; color: #fbbf24;">
                ⚠️ Tasks Pending
            </div>
        </div>
        <div style="padding: 28px;">
            <h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 800; color: #ffffff;">
                Keep Your Momentum Going, {escape(user.full_name or user.username)}!
            </h2>
            <p style="font-size: 14px; color: #cbd5e1; line-height: 1.6; margin-top: 0;">
                You still have <strong>{len(pending_tasks)} pending study task(s)</strong> scheduled for today (<strong>{escape(plan_date_str)}</strong>). Completing even 15-20 minutes of daily practice protects your study streak and reinforces key concepts for your <strong>{escape(user.target_role or 'career goal')}</strong>.
            </p>

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0;">
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Pending Tasks</div>
                    <div style="font-size: 18px; font-weight: 800; color: #fbbf24; margin-top: 4px;">{len(pending_tasks)}</div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Remaining Time</div>
                    <div style="font-size: 18px; font-weight: 800; color: #38bdf8; margin-top: 4px;">~{remaining_mins} min</div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Completed So Far</div>
                    <div style="font-size: 18px; font-weight: 800; color: #34d399; margin-top: 4px;">{len(completed_tasks)}</div>
                </div>
            </div>

            <h3 style="font-size: 14px; font-weight: 700; color: #cbd5e1; margin: 24px 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Remaining Pending Tasks
            </h3>
            <table style="width: 100%; border-collapse: collapse; background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #1e293b; color: #94a3b8; font-size: 11px; text-transform: uppercase; text-align: left;">
                        <th style="padding: 10px 14px;">Task</th>
                        <th style="padding: 10px 14px; text-align: center;">Type</th>
                        <th style="padding: 10px 14px; text-align: center;">Est. Time</th>
                        <th style="padding: 10px 14px; text-align: right;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {task_rows}
                </tbody>
            </table>

            <div style="margin: 28px 0 10px 0; text-align: center;">
                <a href="http://localhost:5173/daily-tasks" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-size: 14px; font-weight: 700; display: inline-block; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4);">
                    Resume Tasks & Complete Your Daily Plan &rarr;
                </a>
            </div>
        </div>
        <div style="padding: 18px 28px; background-color: #0a0f1d; border-top: 1px solid #1e293b; font-size: 11px; color: #64748b; text-align: center; line-height: 1.5;">
            This automated daily study alert was delivered to your verified email: {escape(recipient)}.<br/>
            &copy; Eduoo AI Learning Platform.
        </div>
    </div>
</body>
</html>
"""

        text_body = f"""[Eduoo AI] Daily Study Alert - Pending Tasks Remaining
=====================================================

Hello {user.full_name or user.username},
You have {len(pending_tasks)} pending study tasks for {plan_date_str} (~{remaining_mins} minutes remaining).

Pending Tasks:
{chr(10).join(text_task_lines)}

Resume and finish your tasks now at: http://localhost:5173/daily-tasks
"""

        return cls._send_custom_html_email(recipient=recipient, subject=subject, html_body=html_body, text_body=text_body, sync=sync)

    @classmethod
    def _send_email_task(
        cls,
        notification_id: int,
        recipient: str,
        title: str,
        message: str,
        category: str,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Worker method that formats and sends the actual email."""
        from .models import Notification

        subject = f"[Eduoo AI] {title}"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Eduoo AI <notifications@eduoo.ai>")

        # Generate HTML and Text versions
        html_content = cls._generate_html_template(
            title=title,
            message=message,
            category=category,
            action_url=action_url,
            action_label=action_label,
            metrics=metrics,
        )
        text_content = cls._generate_text_template(
            title=title,
            message=message,
            category=category,
            action_url=action_url,
            action_label=action_label,
            metrics=metrics,
        )

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            # Record success on notification
            try:
                Notification.objects.filter(id=notification_id).update(
                    email_sent=True,
                    email_sent_at=timezone.now(),
                    email_recipient=recipient,
                    email_error=None,
                )
            except Exception:
                pass

            logger.info("Successfully sent real-time notification email to %s for notif #%s", recipient, notification_id)
            return {"success": True, "message": f"Real-time email successfully delivered to {recipient}"}

        except Exception as exc:
            raw_error = str(exc)
            if "535" in raw_error or "BadCredentials" in raw_error:
                error_msg = (
                    "Google rejected the credentials (535 BadCredentials). "
                    "Please ensure: 1) The 16-letter App Password was generated while logged into this exact Gmail account, "
                    "2) 2-Step Verification is active, and 3) Unlock SMTP access at https://accounts.google.com/DisplayUnlockCaptcha."
                )
            else:
                error_msg = raw_error

            logger.error("Failed to send real-time notification email to %s: %s", recipient, raw_error)
            try:
                Notification.objects.filter(id=notification_id).update(
                    email_sent=False,
                    email_recipient=recipient,
                    email_error=error_msg,
                )
            except Exception:
                pass
            if sync:
                return {"success": False, "error": error_msg}
            return {"success": False, "error": error_msg}

    @staticmethod
    def _generate_html_template(
        title: str,
        message: str,
        category: str,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> str:
        cat_badge = {
            "interview_reminder": ("Interview Performance", "#8b5cf6", "🎯"),
            "platform_sync": ("Platform Telemetry", "#10b981", "⚡"),
            "task_reminder": ("Daily Study Goal", "#3b82f6", "📚"),
            "streak_reminder": ("Streak Milestone", "#f59e0b", "🔥"),
            "weekly_summary": ("Weekly Progress", "#ec4899", "📊"),
            "general": ("Notification", "#6366f1", "✨"),
        }.get(category, ("Notification", "#6366f1", "✨"))

        badge_name, badge_color, badge_icon = cat_badge

        # Metrics rows
        metrics_html = ""
        if metrics:
            metric_cards = ""
            for k, v in metrics.items():
                metric_cards += f"""
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 8px; padding: 12px 14px; margin: 4px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #94a3b8; font-weight: 600;">{escape(str(k))}</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-top: 4px; font-family: monospace;">{escape(str(v))}</div>
                </div>
                """
            metrics_html = f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin: 20px 0;">
                {metric_cards}
            </div>
            """

        # Action button
        btn_html = ""
        if action_url:
            label = action_label or "View Details on Eduoo"
            btn_html = f"""
            <div style="margin: 28px 0 10px 0; text-align: center;">
                <a href="{escape(action_url)}" style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-size: 14px; font-weight: 700; display: inline-block; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
                    {escape(label)} &rarr;
                </a>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #090d16; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
    <div style="max-width: 580px; margin: 30px auto; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
        <!-- Top Accent Bar -->
        <div style="height: 4px; background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);"></div>
        
        <!-- Header -->
        <div style="padding: 24px 28px 16px 28px; border-bottom: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: inline-block;">
                <span style="font-size: 20px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff;">Eduoo<span style="color: #6366f1;">.AI</span></span>
                <span style="display: block; font-size: 11px; color: #64748b; font-weight: 500;">Real-Time Learning & Career Telemetry</span>
            </div>
            <div style="display: inline-block; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 700; color: {badge_color};">
                {badge_icon} {badge_name}
            </div>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 28px;">
            <h2 style="margin: 0 0 14px 0; font-size: 20px; font-weight: 800; color: #ffffff; line-height: 1.3;">{escape(title)}</h2>
            <div style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-bottom: 20px;">
                {escape(message)}
            </div>
            
            {metrics_html}
            {btn_html}
        </div>
        
        <!-- Footer -->
        <div style="padding: 18px 28px; background-color: #0a0f1d; border-top: 1px solid #1e293b; font-size: 11px; color: #64748b; text-align: center; line-height: 1.5;">
            You received this real-time notification because email notifications are enabled on your Eduoo account.<br/>
            To customize your notification alert frequency, visit your <a href="http://localhost:5173/profile" style="color: #818cf8; text-decoration: underline;">Profile Settings</a>.
        </div>
    </div>
</body>
</html>
"""
        return html

    @staticmethod
    def _generate_text_template(
        title: str,
        message: str,
        category: str,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> str:
        lines = [
            f"[Eduoo AI] {title}",
            "=" * len(title),
            "",
            message,
            "",
        ]
        if metrics:
            lines.append("Key Metrics:")
            for k, v in metrics.items():
                lines.append(f" - {k}: {v}")
            lines.append("")
        if action_url:
            label = action_label or "View on Eduoo"
            lines.append(f"{label}: {action_url}")
            lines.append("")
        lines.append("---")
        lines.append("Manage your notification preferences at http://localhost:5173/profile")
        return "\n".join(lines)
