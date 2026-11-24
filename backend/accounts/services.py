"""Account domain services for Eduoo."""

from django.contrib.auth import get_user_model
from common.constants import TARGET_ROLES
from .models import UserProfile

User = get_user_model()


class UserService:
    @staticmethod
    def get_supported_target_roles():
        return list(TARGET_ROLES)

    @staticmethod
    def change_password(user, old_password: str, new_password: str):
        if not user.check_password(old_password):
            return False, "Current password does not match."
        user.set_password(new_password)
        user.save()
        return True, "Password updated successfully."

    @staticmethod
    def sync_user_profile(user, profile_data=None):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        fields = [
            "full_name",
            "college",
            "branch",
            "graduation_year",
            "target_role",
            "daily_study_hours",
            "bio",
            "preferred_learning_style",
            "experience_level",
            "career_goal",
        ]
        if profile_data:
            for field in fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
                    setattr(profile, field, profile_data[field])
            user.save()
            profile.save()
        else:
            for field in fields:
                setattr(profile, field, getattr(user, field, None))
            profile.save()
        return profile
