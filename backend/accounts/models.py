from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    target_role = models.CharField(max_length=255, blank=True, null=True)
    daily_study_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    bio = models.TextField(blank=True, null=True)
    preferred_learning_style = models.CharField(max_length=255, blank=True, null=True)
    experience_level = models.CharField(max_length=255, blank=True, null=True)
    career_goal = models.TextField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["target_role"]),
        ]

    def __str__(self):
        return self.email


class EmailVerificationOTP(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="email_otps")
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "otp_code"]),
            models.Index(fields=["email", "is_used"]),
        ]

    def __str__(self):
        return f"OTP for {self.email} ({'used' if self.is_used else 'active'})"



class UserProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    target_role = models.CharField(max_length=255, blank=True, null=True)
    daily_study_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    bio = models.TextField(blank=True, null=True)
    preferred_learning_style = models.CharField(max_length=255, blank=True, null=True)
    experience_level = models.CharField(max_length=255, blank=True, null=True)
    career_goal = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["target_role"]),
            models.Index(fields=["college"]),
        ]

    def __str__(self):
        return f"Profile for {self.user.email}"
