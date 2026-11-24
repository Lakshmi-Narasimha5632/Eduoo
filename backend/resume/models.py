"""Resume models supporting parsed PDF data, editable fields, and ATS analysis."""

from django.conf import settings
from django.db import models


class ResumeSnapshot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resume_snapshots")
    file = models.FileField(upload_to="resumes/", null=True, blank=True)
    raw_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    target_role = models.CharField(max_length=255, blank=True, null=True)
    parsed_data = models.JSONField(default=dict, blank=True)
    ats_score = models.PositiveSmallIntegerField(default=70)
    ats_analysis = models.JSONField(default=dict, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    skill_gaps = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Resume snapshot for {self.user.email} ({self.target_role or 'General'})"
