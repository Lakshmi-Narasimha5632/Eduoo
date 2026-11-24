from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AIEvaluationResult


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def ai_evaluation_view(request):
    if request.method == "POST":
        prompt = request.data.get("prompt") or "Assess my interview readiness."
        context = request.data.get("context") or ""

        if not prompt.strip():
            return Response({"detail": "prompt is required."}, status=status.HTTP_400_BAD_REQUEST)

        context_score = min(100, max(55, 60 + len(context.split()) // 5))
        overall_score = min(100, max(65, context_score - 5))
        strengths = [
            "Strong execution evidence",
            "Good project ownership",
            "Consistent problem-solving mindset",
        ]
        improvement_areas = [
            "System design depth",
            "Communication structure",
            "Handling ambiguity",
        ]
        summary = (
            "You show good readiness for target-role interviews with strong project evidence and problem-solving habits. "
            "The biggest gain would come from improving system-design explanation and structured communication."
        )

        result = AIEvaluationResult.objects.create(
            user=request.user,
            prompt=prompt,
            context=context,
            overall_score=overall_score,
            summary=summary,
            strengths=strengths,
            improvement_areas=improvement_areas,
        )

        return Response(
            {
                "id": result.id,
                "overall_score": result.overall_score,
                "summary": result.summary,
                "strengths": result.strengths,
                "improvement_areas": result.improvement_areas,
            }
        )

    latest = AIEvaluationResult.objects.filter(user=request.user).order_by("-created_at").first()
    if latest:
        return Response(
            {
                "overall_score": latest.overall_score,
                "strengths": latest.strengths,
                "improvement_areas": latest.improvement_areas,
                "summary": latest.summary,
            }
        )

    return Response(
        {
            "overall_score": 82,
            "strengths": [
                "Strong problem-solving foundation",
                "Clear project experience",
                "Consistent study habits",
            ],
            "improvement_areas": [
                "System design depth",
                "Mock interview pacing",
                "Advanced backend tradeoff explanation",
            ],
            "summary": "You are on track for interview readiness with a strong basis in coding and project work.",
        }
    )
