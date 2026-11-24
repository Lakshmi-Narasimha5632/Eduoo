from django.conf import settings
from django.db import models


class SkillGap(models.Model):
    SEVERITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skill_gaps")
    skill = models.CharField(max_length=255)
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default="medium")
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-severity", "-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.skill}"
