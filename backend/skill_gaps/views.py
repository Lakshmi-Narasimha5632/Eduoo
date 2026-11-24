from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SkillGap


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def skill_gaps_view(request):
    user = request.user

    if request.method == "POST":
        skill = request.data.get("skill", "").strip()
        severity = request.data.get("severity", "medium")
        reason = request.data.get("reason", "")

        if not skill:
            return Response({"detail": "skill is required."}, status=status.HTTP_400_BAD_REQUEST)

        gap = SkillGap.objects.create(user=user, skill=skill, severity=severity, reason=reason)
        return Response(
            {
                "id": gap.id,
                "skill": gap.skill,
                "severity": gap.severity,
                "reason": gap.reason,
                "created_at": gap.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )

    gaps = SkillGap.objects.filter(user=user)
    items = [
        {
            "id": item.id,
            "skill": item.skill,
            "severity": item.severity,
            "reason": item.reason,
        }
        for item in gaps
    ]

    summary = {
        "total": len(items),
        "high_priority": sum(1 for item in items if item["severity"] == "high"),
        "medium_priority": sum(1 for item in items if item["severity"] == "medium"),
    }

    recommended_focus = "System Design" if summary["high_priority"] else "Data Structures and Algorithms"

    return Response(
        {
            "summary": summary,
            "skill_gaps": items,
            "recommended_focus": recommended_focus,
        }
    )
