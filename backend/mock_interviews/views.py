from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MockInterviewSession


QUESTION_BANK = [
    "Explain a project where you improved backend performance.",
    "How do you design a scalable API for a growing user base?",
    "Describe a time you debugged a production issue under pressure.",
]


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def mock_interviews_view(request):
    if request.method == "POST":
        question = request.data.get("question") or "Explain your approach to system design."
        answer = request.data.get("answer") or ""

        if not answer.strip():
            return Response({"detail": "answer is required."}, status=status.HTTP_400_BAD_REQUEST)

        word_count = len(answer.split())
        score = min(100, max(50, int((word_count / max(1, len(question.split()))) * 18 + 55)))
        feedback = "Strong communication and practical reasoning. Focus on clearer tradeoff explanations and example-driven structure."

        session = MockInterviewSession.objects.create(
            user=request.user,
            question=question,
            answer=answer,
            score=score,
            feedback=feedback,
        )

        return Response(
            {
                "id": session.id,
                "question": session.question,
                "score": session.score,
                "feedback": session.feedback,
            }
        )

    return Response({"questions": QUESTION_BANK})
