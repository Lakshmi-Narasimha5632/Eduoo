"""Serializers for skills and user skills."""

from rest_framework import serializers
from .models import RoleRequirement, Skill, UserSkill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "category", "description"]


class UserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    category = serializers.CharField(source="skill.category", read_only=True)

    class Meta:
        model = UserSkill
        fields = ["id", "skill", "skill_name", "category", "current_level", "target_level", "evidence", "confidence"]


class RoleRequirementSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = RoleRequirement
        fields = ["id", "role_name", "skill", "skill_name", "required_level", "is_mandatory"]
