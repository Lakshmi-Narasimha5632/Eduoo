from django.conf import settings
from django.core.signing import Signer
from django.db import models
from django.utils import timezone


PLATFORM_CHOICES = [
    ("leetcode", "LeetCode"),
    ("github", "GitHub"),
    ("duolingo", "Duolingo"),
    ("linkedin", "LinkedIn"),
    ("hackerrank", "HackerRank"),
    ("codechef", "CodeChef"),
]


class ConnectedPlatform(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="connected_platforms")
    platform = models.CharField(max_length=32, choices=PLATFORM_CHOICES)
    username = models.CharField(max_length=255, blank=True, null=True)
    connected = models.BooleanField(default=False)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    sync_status = models.CharField(max_length=32, default="not_started")
    sync_error = models.TextField(blank=True, null=True)
    cached_analytics = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "platform")
        indexes = [
            models.Index(fields=["user", "platform"]),
            models.Index(fields=["connected", "sync_status"]),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.platform}"

    def set_access_token(self, value):
        if value is None or value == "":
            self.access_token = None
            return
        signer = Signer(salt="eduoo.platform.token")
        self.access_token = signer.sign(value)

    def get_access_token(self):
        if not self.access_token:
            return None
        try:
            signer = Signer(salt="eduoo.platform.token")
            return signer.unsign(self.access_token)
        except Exception:
            return None

    def set_refresh_token(self, value):
        if value is None or value == "":
            self.refresh_token = None
            return
        signer = Signer(salt="eduoo.platform.refresh")
        self.refresh_token = signer.sign(value)

    def get_refresh_token(self):
        if not self.refresh_token:
            return None
        try:
            signer = Signer(salt="eduoo.platform.refresh")
            return signer.unsign(self.refresh_token)
        except Exception:
            return None

    def mark_synced(self, *, status="success", error=None):
        self.sync_status = status
        self.sync_error = error
        self.save(update_fields=["sync_status", "sync_error", "last_synced_at", "connected", "updated_at"])


class LeetCodeCatalogProblem(models.Model):
    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES)
    topics = models.JSONField(default=list, blank=True)
    problem_url = models.URLField(max_length=500, blank=True)
    external_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["external_id", "title"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["difficulty"]),
        ]

    def __str__(self):
        return f"{self.external_id or ''} {self.title} ({self.difficulty})".strip()


class LeetCodeUserSolvedProblem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leetcode_solved_problems")
    problem = models.ForeignKey(LeetCodeCatalogProblem, on_delete=models.SET_NULL, null=True, blank=True, related_name="solved_by_users")
    problem_slug = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=16, default="Medium")
    solved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "problem_slug")
        ordering = ["-solved_at"]
        indexes = [
            models.Index(fields=["user", "difficulty"]),
            models.Index(fields=["user", "-solved_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.difficulty})"

