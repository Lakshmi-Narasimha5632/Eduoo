"""Daily task services for Eduoo."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, Optional
from django.utils import timezone

from notifications.services import NotificationService
from .models import DailyTask, DailyTaskPlan
from .planners import AdaptiveDailyTaskPlanner

logger = logging.getLogger(__name__)


class DailyTaskPlanner(AdaptiveDailyTaskPlanner):
    """Planner service extending AdaptiveDailyTaskPlanner for backward compatibility."""
    pass


class DailyTaskReportService:
    """Automated email reporting service for daily study plans and tasks."""

    @classmethod
    def send_completion_report(
        cls,
        plan: DailyTaskPlan,
        force: bool = False,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches an automated Daily Task Completion Report to the user's verified email."""
        user = plan.user
        if not user.email:
            return {"success": False, "error": "User does not have an email address."}

        # Check if already sent unless forced
        if plan.completion_report_sent and not force:
            logger.info("Daily completion report already sent for user %s on %s", user.email, plan.date)
            return {
                "success": True,
                "already_sent": True,
                "message": f"Completion report was already sent to {user.email} on {plan.completion_report_sent_at}.",
            }

        res = NotificationService.send_task_completion_report(
            user=user,
            plan=plan,
            sync=sync,
        )

        plan.completion_report_sent = True
        plan.completion_report_sent_at = timezone.now()
        plan.save(update_fields=["completion_report_sent", "completion_report_sent_at", "updated_at"])

        # Also register in-app notification
        try:
            NotificationService.create_notification(
                user=user,
                title="Daily Study Plan Completed! 🌟",
                message=f"Awesome work! You completed all tasks in your daily plan today, logging {plan.completed_minutes} minutes of focused learning.",
                category="task_reminder",
                send_email=False,
                action_url="http://localhost:5173/daily-tasks",
                action_label="View Daily Tasks & Streaks",
            )
        except Exception:
            pass

        return {
            "success": True,
            "report_type": "completion",
            "recipient": user.email,
            "message": f"Daily task completion report dispatched to {user.email}!",
            "details": res,
        }

    @classmethod
    def send_incomplete_alert(
        cls,
        plan: DailyTaskPlan,
        force: bool = False,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches an automated incomplete tasks alert email to the user's verified email."""
        user = plan.user
        if not user.email:
            return {"success": False, "error": "User does not have an email address."}

        # Check if already sent today unless forced
        if plan.incomplete_alert_sent and not force:
            logger.info("Daily incomplete alert already sent for user %s on %s", user.email, plan.date)
            return {
                "success": True,
                "already_sent": True,
                "message": f"Incomplete tasks alert was already sent to {user.email} on {plan.incomplete_alert_sent_at}.",
            }

        pending_tasks = plan.tasks.exclude(status="completed")
        if not pending_tasks.exists():
            return {"success": False, "message": "All tasks are already completed for this plan."}

        res = NotificationService.send_task_incomplete_alert(
            user=user,
            plan=plan,
            sync=sync,
        )

        plan.incomplete_alert_sent = True
        plan.incomplete_alert_sent_at = timezone.now()
        plan.save(update_fields=["incomplete_alert_sent", "incomplete_alert_sent_at", "updated_at"])

        # In-app notification
        try:
            NotificationService.create_notification(
                user=user,
                title="Daily Tasks Remaining ⚠️",
                message=f"You have {pending_tasks.count()} pending study task(s) remaining for today. Resume practice to keep your streak!",
                category="task_reminder",
                send_email=False,
                action_url="http://localhost:5173/daily-tasks",
                action_label="Complete Today's Tasks",
            )
        except Exception:
            pass

        return {
            "success": True,
            "report_type": "incomplete_alert",
            "recipient": user.email,
            "message": f"Incomplete tasks alert dispatched to {user.email}!",
            "details": res,
        }

    @classmethod
    def send_daily_status(
        cls,
        user,
        target_date: Optional[date] = None,
        force: bool = False,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Inspects user's task plan for the date and sends completion or incomplete report accordingly."""
        check_date = target_date or timezone.now().date()
        plan = DailyTaskPlanner.get_or_create_plan(user, check_date)

        if not plan.tasks.exists():
            plan = DailyTaskPlanner.generate_for_user(user, check_date)

        total_tasks = plan.tasks.count()
        incomplete_tasks = plan.tasks.exclude(status="completed")

        if total_tasks > 0 and not incomplete_tasks.exists():
            return cls.send_completion_report(plan, force=force, sync=sync)
        else:
            return cls.send_incomplete_alert(plan, force=force, sync=sync)

