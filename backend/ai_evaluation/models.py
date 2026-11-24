from django.conf import settings
from django.db import models


class AIEvaluationResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_evaluations")
    prompt = models.TextField(blank=True)
    context = models.TextField(blank=True)
    overall_score = models.PositiveIntegerField(default=0)
    summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    improvement_areas = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI evaluation for {self.user.email}"
