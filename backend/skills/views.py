"""API views for skills, skill gaps, and career readiness."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Skill, UserSkill
from .serializers import SkillSerializer, UserSkillSerializer
from .services import SkillService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_list_view(request):
    SkillService.seed_taxonomy()
    category = request.query_params.get("category")
    qs = Skill.objects.all()
    if category:
        qs = qs.filter(category__iexact=category)
    return Response({"success": True, "skills": SkillSerializer(qs, many=True).data})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_skills_view(request):
    SkillService.seed_taxonomy()
    user = request.user

    if request.method == "POST":
        skill_name = request.data.get("skill_name")
        level = request.data.get("current_level", 2)
        if not skill_name:
            return Response(
                {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "skill_name is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        skill, _ = Skill.objects.get_or_create(name=skill_name.strip(), defaults={"category": "Custom"})
        user_skill, _ = UserSkill.objects.update_or_create(
            user=user,
            skill=skill,
            defaults={"current_level": int(level), "source_platform": "user_input"},
        )
        return Response({"success": True, "skill": UserSkillSerializer(user_skill).data})

    qs = UserSkill.objects.filter(user=user)
    return Response({"success": True, "skills": UserSkillSerializer(qs, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skill_gap_analysis_view(request):
    data = SkillService.analyze_skill_gaps(request.user)
    return Response({"success": True, **data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def career_readiness_view(request):
    readiness = SkillService.calculate_career_readiness(request.user)
    return Response({"success": True, **readiness})
