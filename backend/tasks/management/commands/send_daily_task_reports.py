"""Django management command to dispatch daily task reports to verified user emails."""

import logging
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import DailyTaskPlan
from tasks.services import DailyTaskPlanner, DailyTaskReportService

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Dispatches daily task completion reports or incomplete alerts to verified user emails."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Target date in YYYY-MM-DD format (defaults to today).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-dispatch even if report was already sent today.",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Filter by user email or username.",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Send emails synchronously instead of in background thread pool.",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Invalid date format '{date_str}'. Use YYYY-MM-DD."))
                return
        else:
            target_date = timezone.now().date()

        force = options.get("force", False)
        sync = options.get("sync", False)
        user_filter = options.get("user")

        users_qs = User.objects.filter(is_active=True, is_email_verified=True).exclude(email="")
        if user_filter:
            users_qs = users_qs.filter(email__iexact=user_filter) | users_qs.filter(username__iexact=user_filter)

        self.stdout.write(
            self.style.NOTICE(
                f"Starting Daily Task Report Dispatcher for {target_date} ({users_qs.count()} verified user(s))..."
            )
        )

        success_count = 0
        skipped_count = 0
        error_count = 0

        for user in users_qs:
            try:
                plan = DailyTaskPlanner.get_or_create_plan(user, target_date)
                if not plan.tasks.exists():
                    plan = DailyTaskPlanner.generate_for_user(user, target_date)

                total_tasks = plan.tasks.count()
                incomplete_tasks = plan.tasks.exclude(status="completed")

                if total_tasks > 0 and not incomplete_tasks.exists():
                    res = DailyTaskReportService.send_completion_report(plan, force=force, sync=sync)
                    report_type = "Completion Report"
                else:
                    res = DailyTaskReportService.send_incomplete_alert(plan, force=force, sync=sync)
                    report_type = "Incomplete Tasks Alert"

                if res.get("already_sent"):
                    skipped_count += 1
                    self.stdout.write(f" - [{user.email}] {report_type}: already sent ({res.get('message')})")
                elif res.get("success"):
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f" - [{user.email}] {report_type}: dispatched successfully."))
                else:
                    error_count += 1
                    self.stdout.write(self.style.WARNING(f" - [{user.email}] {report_type}: skipped/error ({res.get('error') or res.get('message')})"))

            except Exception as exc:
                error_count += 1
                self.stderr.write(self.style.ERROR(f" - [{user.email}] Error: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished: {success_count} sent, {skipped_count} skipped, {error_count} error(s)."
            )
        )
