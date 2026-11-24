from django.conf import settings
from django.db import models


class Recommendation(models.Model):
    CATEGORY_CHOICES = [
        ("coding", "coding"),
        ("project", "project"),
        ("interview", "interview"),
        ("resume", "resume"),
        ("platform", "platform"),
        ("skills", "skills"),
        ("career", "career"),
        ("study", "study"),
        ("skill_gap", "skill_gap"),
    ]
    PRIORITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations")
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="medium")
    title = models.CharField(max_length=255)
    description = models.TextField()
    action = models.TextField()
    estimated_time = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.title}"
