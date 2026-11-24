"""Models for normalized skills, user proficiency, and role requirements."""

from django.conf import settings
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=128, unique=True)
    category = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"


class UserSkill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="user_skills")
    current_level = models.PositiveSmallIntegerField(default=1)  # 1: Beginner, 2: Intermediate, 3: Advanced
    target_level = models.PositiveSmallIntegerField(default=2)
    evidence = models.JSONField(default=list, blank=True)
    source_platform = models.CharField(max_length=32, blank=True, null=True)  # leetcode, github, resume, etc.
    confidence = models.PositiveSmallIntegerField(default=75)  # 0 to 100%
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "skill")
        ordering = ["-current_level", "skill__name"]
        indexes = [
            models.Index(fields=["user", "current_level"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.skill.name} (Lv {self.current_level})"


class RoleRequirement(models.Model):
    role_name = models.CharField(max_length=128)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="role_requirements")
    required_level = models.PositiveSmallIntegerField(default=2)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = ("role_name", "skill")
        ordering = ["role_name", "-is_mandatory"]

    def __str__(self):
        return f"{self.role_name} -> {self.skill.name} (Lv {self.required_level})"
