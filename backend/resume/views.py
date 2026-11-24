"""Resume API views handling upload, overview, editing extracted data, and ATS analysis."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .parser import ResumeParser
from .services import ResumeService


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def resume_overview(request):
    user = request.user

    if request.method == "PATCH":
        allowed_fields = {
            "full_name",
            "email",
            "target_role",
            "college",
            "branch",
            "graduation_year",
            "experience_level",
            "bio",
            "career_goal",
        }

        updated_fields = []
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                updated_fields.append(field)
        if updated_fields:
            user.save(update_fields=updated_fields)

    snapshot = ResumeService.get_latest_snapshot(user)
    parsed = snapshot.parsed_data or {}

    profile = {
        "full_name": user.full_name or parsed.get("full_name") or parsed.get("name") or "",
        "email": user.email or parsed.get("email") or "",
        "phone": getattr(user, "phone", "") or parsed.get("phone") or "",
        "target_role": user.target_role or snapshot.target_role or "Full Stack Developer",
        "college": user.college,
        "branch": user.branch,
        "graduation_year": user.graduation_year,
        "experience_level": user.experience_level,
        "bio": user.bio,
        "career_goal": user.career_goal,
    }

    file_name = snapshot.file.name.split("/")[-1] if snapshot.file else None

    return Response({
        "success": True,
        "profile": profile,
        "strengths": snapshot.strengths,
        "skill_gaps": snapshot.skill_gaps,
        "ats_score": snapshot.ats_score,
        "ats_analysis": snapshot.ats_analysis,
        "parsed_data": snapshot.parsed_data,
        "target_role": snapshot.target_role or profile["target_role"],
        "file_name": file_name,
        "has_file": bool(snapshot.file),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def resume_upload_view(request):
    """Upload and parse resume PDF endpoint."""
    file_obj = request.FILES.get("resume") or request.FILES.get("file")
    if not file_obj:
        return Response(
            {"success": False, "error": {"code": "MISSING_FILE", "message": "Please upload a resume file (PDF)."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not file_obj.name.lower().endswith(".pdf"):
        return Response(
            {"success": False, "error": {"code": "INVALID_FORMAT", "message": "Only PDF files are supported initially."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    snapshot = ResumeService.process_file_upload(request.user, file_obj)
    file_name = snapshot.file.name.split("/")[-1] if snapshot.file else file_obj.name

    return Response({
        "success": True,
        "message": "Resume uploaded and analyzed successfully.",
        "ats_score": snapshot.ats_score,
        "parsed_data": snapshot.parsed_data,
        "ats_analysis": snapshot.ats_analysis,
        "strengths": snapshot.strengths,
        "skill_gaps": snapshot.skill_gaps,
        "target_role": snapshot.target_role,
        "file_name": file_name,
        "has_file": bool(snapshot.file),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resume_analyze_view(request):
    """Section 20 ATS analysis endpoint."""
    user = request.user
    target_role = request.data.get("target_role") or user.target_role or "Full Stack Developer"
    snapshot = ResumeService.get_latest_snapshot(user)
    parsed = snapshot.parsed_data or {}

    analysis = ResumeParser.analyze_ats(parsed, target_role=target_role)
    snapshot.ats_score = analysis["ats_score"]
    snapshot.ats_analysis = analysis
    snapshot.target_role = target_role
    snapshot.strengths = analysis["matched_skills"]
    snapshot.skill_gaps = analysis["missing_skills"]
    snapshot.save()

    return Response({
        "success": True,
        "ats_score": snapshot.ats_score,
        "ats_analysis": snapshot.ats_analysis,
        "parsed_data": snapshot.parsed_data,
        "strengths": snapshot.strengths,
        "skill_gaps": snapshot.skill_gaps,
        "target_role": snapshot.target_role,
        **analysis,
    })


@api_view(["PUT", "POST"])
@permission_classes([IsAuthenticated])
def resume_edit_parsed_view(request):
    """Allow user to edit extracted data per Section 20."""
    data = request.data.get("parsed_data") or request.data
    snapshot = ResumeService.update_parsed_data(request.user, data)
    return Response({
        "success": True,
        "message": "Resume data updated successfully.",
        "parsed_data": snapshot.parsed_data,
        "ats_score": snapshot.ats_score,
        "ats_analysis": snapshot.ats_analysis,
        "strengths": snapshot.strengths,
        "skill_gaps": snapshot.skill_gaps,
        "target_role": snapshot.target_role,
    })
