from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from platforms.models import ConnectedPlatform
from .models import Recommendation
from .serializers import RecommendationSerializer


def _synthesize_user_recommendations(user):
    role = user.target_role or "Software Developer"
    connected_plats = ConnectedPlatform.objects.filter(user=user, connected=True)
    has_leetcode = connected_plats.filter(platform="leetcode").exists()
    has_hackerrank = connected_plats.filter(platform="hackerrank").exists()
    has_codechef = connected_plats.filter(platform="codechef").exists()

    generated = []

    # 1. Coding: Algorithm & Problem Solving
    rec1, _ = Recommendation.objects.get_or_create(
        user=user,
        title=f"Practice 3 Medium {role} Interview Questions",
        defaults={
            "category": "coding",
            "priority": "high",
            "description": f"Target high-frequency algorithm patterns for {role} roles: Sliding Window, Tree Traversals, and Dynamic Programming.",
            "action": "Mastering these patterns directly increases problem-solving score on your career readiness assessment.",
            "estimated_time": 45,
        },
    )
    generated.append(rec1)

    # 2. Project: Portfolio Project Architecture
    rec2, _ = Recommendation.objects.get_or_create(
        user=user,
        title=f"Add End-to-End Testing & Docker to Your {role} Project",
        defaults={
            "category": "project",
            "priority": "medium",
            "description": "Recruiters and hiring managers heavily favor candidates whose GitHub repositories feature automated tests and containerization.",
            "action": "Elevates your Projects & Portfolio readiness index from intermediate to competitive tier.",
            "estimated_time": 60,
        },
    )
    generated.append(rec2)

    # 3. Interview: Interactive AI Mock Interview
    rec3, _ = Recommendation.objects.get_or_create(
        user=user,
        title=f"Complete a 15-minute {role} Mock Interview Round",
        defaults={
            "category": "interview",
            "priority": "high",
            "description": "Simulate real behavioral and technical interview questions to practice clear verbal communication and STAR structuring.",
            "action": "Directly evaluates Technical Accuracy, Clarity, and Confidence metrics.",
            "estimated_time": 15,
        },
    )
    generated.append(rec3)

    # 4. Resume: ATS Polish & Impact Metrics
    rec4, _ = Recommendation.objects.get_or_create(
        user=user,
        title="Quantify Accomplishments on Your Resume",
        defaults={
            "category": "resume",
            "priority": "medium",
            "description": "Update bullet points with metrics (e.g. 'Improved query latency by 40%', 'Handled 10k daily requests') to pass modern ATS screening.",
            "action": "Increases ATS match score and section parsability for tech employers.",
            "estimated_time": 30,
        },
    )
    generated.append(rec4)

    # 5. Platform: Competitive Coding Badges
    rec5, _ = Recommendation.objects.get_or_create(
        user=user,
        title="Earn 5-Star Problem Solving Badge on HackerRank",
        defaults={
            "category": "platform",
            "priority": "medium",
            "description": "Domain badges on HackerRank and CodeChef provide verifiable third-party validation of coding agility.",
            "action": "Synchronizes into unified platform telemetry and boosts competitive rating tier.",
            "estimated_time": 40,
        },
    )
    generated.append(rec5)

    # 6. Skills: Modern Framework Fundamentals
    rec6, _ = Recommendation.objects.get_or_create(
        user=user,
        title=f"Master Asynchronous Architecture & Caching for {role}",
        defaults={
            "category": "skills",
            "priority": "high",
            "description": f"Understanding async event loops, background worker queues, and Redis caching is standard criteria for {role} interviews.",
            "action": "Fills technical architecture gaps flagged in your skills profile.",
            "estimated_time": 50,
        },
    )
    generated.append(rec6)

    return generated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommendations_list(request):
    queryset = Recommendation.objects.filter(user=request.user).order_by("-created_at")
    if not queryset.exists():
        _synthesize_user_recommendations(request.user)
        queryset = Recommendation.objects.filter(user=request.user).order_by("-created_at")

    category_filter = request.query_params.get("category", "").strip().lower()
    status_filter = request.query_params.get("status", "").strip().lower()
    priority_filter = request.query_params.get("priority", "").strip().lower()

    all_data = RecommendationSerializer(queryset, many=True).data

    filtered = []
    category_counts = {}
    for item in all_data:
        cat = (item.get("category") or "general").lower()
        category_counts[cat] = category_counts.get(cat, 0) + 1

        if category_filter and category_filter != "all" and cat != category_filter:
            continue
        if status_filter and status_filter != "all" and (item.get("status") or "").lower() != status_filter:
            continue
        if priority_filter and priority_filter != "all" and (item.get("priority") or "").lower() != priority_filter:
            continue
        filtered.append(item)

    return Response({
        "success": True,
        "recommendations": filtered,
        "total_count": len(all_data),
        "filtered_count": len(filtered),
        "categories": category_counts,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_recommendations_view(request):
    _synthesize_user_recommendations(request.user)
    queryset = Recommendation.objects.filter(user=request.user).order_by("-created_at")
    serializer = RecommendationSerializer(queryset, many=True)
    return Response({"success": True, "recommendations": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_recommendation_status(request, recommendation_id):
    try:
        recommendation = Recommendation.objects.get(id=recommendation_id, user=request.user)
    except Recommendation.DoesNotExist:
        return Response(
            {"success": False, "error": {"code": "NOT_FOUND", "message": "Recommendation not found."}},
            status=status.HTTP_404_NOT_FOUND,
        )

    new_status = request.data.get("status", "in_progress")
    if new_status == "dismissed":
        recommendation.delete()
        return Response({"success": True, "message": "Recommendation dismissed."})

    recommendation._status = new_status
    serializer = RecommendationSerializer(recommendation)
    data = serializer.data
    data["status"] = new_status
    return Response({"success": True, "recommendation": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_recommendation(request):
    serializer = RecommendationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    recommendation = serializer.save(user=request.user)
    return Response({"success": True, "recommendation": RecommendationSerializer(recommendation).data}, status=status.HTTP_201_CREATED)

