from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
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


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
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
            "is_email_verified",
            "profile",
        ]
        read_only_fields = ["id", "is_email_verified"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
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
            "profile",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        profile_data = validated_data.pop("profile", {})

        user = User.objects.create_user(password=password, **validated_data)

        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(
                user=user,
                full_name=user.full_name,
                college=user.college,
                branch=user.branch,
                graduation_year=user.graduation_year,
                target_role=user.target_role,
                daily_study_hours=user.daily_study_hours,
                bio=user.bio,
                preferred_learning_style=user.preferred_learning_style,
                experience_level=user.experience_level,
                career_goal=user.career_goal,
            )

        return user

    def update(self, instance, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password", None)
        profile_data = validated_data.pop("profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if profile_data or not hasattr(instance, "profile"):
            UserProfile.objects.update_or_create(
                user=instance,
                defaults=profile_data or {
                    "full_name": instance.full_name,
                    "college": instance.college,
                    "branch": instance.branch,
                    "graduation_year": instance.graduation_year,
                    "target_role": instance.target_role,
                    "daily_study_hours": instance.daily_study_hours,
                    "bio": instance.bio,
                    "preferred_learning_style": instance.preferred_learning_style,
                    "experience_level": instance.experience_level,
                    "career_goal": instance.career_goal,
                },
            )

        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("email") or attrs.get("username")
        if not identifier or not identifier.strip():
            raise serializers.ValidationError({"email": "Email or username is required."})
        attrs["identifier"] = identifier.strip()
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
