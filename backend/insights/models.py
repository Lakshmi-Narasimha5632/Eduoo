from django.conf import settings
from django.db import models


class Insight(models.Model):
    INSIGHT_TYPES = [
        ("coding", "coding"),
        ("platform", "platform"),
        ("skills", "skills"),
        ("projects", "projects"),
        ("performance", "performance"),
        ("consistency", "consistency"),
        ("difficulty", "difficulty"),
        ("topic", "topic"),
        ("activity", "activity"),
        ("progress", "progress"),
        ("recommendation", "recommendation"),
        ("career", "career"),
        ("interview", "interview"),
        ("skill_gap", "skill_gap"),
    ]
    PRIORITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="insights")
    type = models.CharField(max_length=32, choices=INSIGHT_TYPES)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="medium")
    title = models.CharField(max_length=255)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.title}"
