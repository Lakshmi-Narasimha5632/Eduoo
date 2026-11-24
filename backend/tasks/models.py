from django.conf import settings
from django.db import models


class DailyTaskPlan(models.Model):
    STATUS_CHOICES = [
        ("planned", "planned"),
        ("in_progress", "in_progress"),
        ("completed", "completed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_task_plans")
    date = models.DateField()
    total_minutes = models.PositiveIntegerField(default=0)
    completed_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="planned")
    completion_report_sent = models.BooleanField(default=False)
    completion_report_sent_at = models.DateTimeField(null=True, blank=True)
    incomplete_alert_sent = models.BooleanField(default=False)
    incomplete_alert_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.email} - {self.date}"


class DailyTask(models.Model):
    TASK_TYPE_CHOICES = [
        ("leetcode", "leetcode"),
        ("github", "github"),
        ("language", "language"),
        ("interview", "interview"),
        ("general", "general"),
    ]
    STATUS_CHOICES = [
        ("pending", "pending"),
        ("completed", "completed"),
    ]
    PRIORITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    plan = models.ForeignKey(DailyTaskPlan, on_delete=models.CASCADE, related_name="tasks")
    task_type = models.CharField(max_length=32, choices=TASK_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=255, blank=True)
    difficulty = models.CharField(max_length=32, blank=True, null=True)
    estimated_minutes = models.PositiveIntegerField(default=30)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    problem_url = models.URLField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "-estimated_minutes"]

    def __str__(self):
        return self.title
