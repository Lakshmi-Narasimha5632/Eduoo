from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from platforms.models import ConnectedPlatform
from .models import Insight
from .serializers import InsightSerializer


def _synthesize_user_insights(user):
    """Dynamically generate insights across distinct categories based on user activity and connected platforms."""
    role = user.target_role or "Software Developer"
    connected_plats = ConnectedPlatform.objects.filter(user=user, connected=True)
    has_leetcode = connected_plats.filter(platform="leetcode").exists()
    has_github = connected_plats.filter(platform="github").exists()
    has_hackerrank = connected_plats.filter(platform="hackerrank").exists()
    has_codechef = connected_plats.filter(platform="codechef").exists()

    generated = []

    # 1. Career Category: Role alignment
    ins_career, _ = Insight.objects.get_or_create(
        user=user,
        title=f"{role} Technical Bar & System Architecture",
        defaults={
            "type": "career",
            "priority": "high",
            "message": f"Your career profile is aligned with {role}. Ensure you balance algorithm problem solving with real-world system design, APIs, and clean architectural patterns.",
            "metadata": {
                "category": "career",
                "platform": "eduoo_ai",
                "action_items": [
                    f"Complete 2 Medium-level algorithm problems tailored to {role} hiring bars.",
                    "Review core system design principles: caching, relational database indexing, and REST APIs.",
                ],
            },
        },
    )
    generated.append(ins_career)

    # 2. Coding Category: Algorithm mastery & difficulty balance
    ins_coding, _ = Insight.objects.get_or_create(
        user=user,
        title="Elevate Medium to Hard Problem Ratio for Tier-1 Readiness",
        defaults={
            "type": "coding",
            "priority": "high",
            "message": "Senior engineering interview bars evaluate edge-case handling under ambiguity. Transitioning from standard Easy questions to Medium/Hard questions will noticeably boost your readiness score.",
            "metadata": {
                "category": "coding",
                "platform": "leetcode" if has_leetcode else "eduoo_ai",
                "action_items": [
                    "Target Sliding Window and Dynamic Programming patterns this week.",
                    "Time yourself strictly to 25 minutes per Medium problem.",
                ],
            },
        },
    )
    generated.append(ins_coding)

    # 3. Platform Category: Telemetry & badge synchronization
    if not has_hackerrank and not has_codechef:
        ins_plat, _ = Insight.objects.get_or_create(
            user=user,
            title="Connect Competitive Coding Platforms (HackerRank / CodeChef)",
            defaults={
                "type": "platform",
                "priority": "medium",
                "message": "Linking HackerRank or CodeChef validates your contest ratings, topic badges, and speed under time pressure.",
                "metadata": {
                    "category": "platform",
                    "platform": "hackerrank",
                    "action_items": [
                        "Link your HackerRank username to sync skill badges and domain stars.",
                        "Link your CodeChef handle to track competitive division rating.",
                    ],
                },
            },
        )
        generated.append(ins_plat)
    else:
        ins_plat_active, _ = Insight.objects.get_or_create(
            user=user,
            title="Competitive Coding Telemetry Synchronized",
            defaults={
                "type": "platform",
                "priority": "low",
                "message": "Real-time sync is active for your competitive profiles. Badges and solved problems are feeding into unified readiness telemetry.",
                "metadata": {
                    "category": "platform",
                    "platform": "hackerrank" if has_hackerrank else "codechef",
                    "action_items": [
                        "Participate in the next weekend contest round to boost rating.",
                    ],
                },
            },
        )
        generated.append(ins_plat_active)

    if not has_github:
        ins_git, _ = Insight.objects.get_or_create(
            user=user,
            title="Showcase Your Codebase & Project Portfolio on GitHub",
            defaults={
                "type": "projects",
                "priority": "medium",
                "message": "Code quality and commit history contribute 25% to hiring managers' assessment. Connect GitHub to verify repository complexity and CI/CD pipelines.",
                "metadata": {
                    "category": "projects",
                    "platform": "github",
                    "action_items": [
                        "Link your GitHub account in the Platforms tab.",
                        "Pin your top full-stack repository with clear README documentation.",
                    ],
                },
            },
        )
        generated.append(ins_git)

    # 4. Interview Category: Mock Interview Verbal Readiness
    ins_interview, _ = Insight.objects.get_or_create(
        user=user,
        title="Simulate Real Behavioral & Technical Interviews with Eduoo AI",
        defaults={
            "type": "interview",
            "priority": "high",
            "message": "Strong technical candidates often fall short on structured verbal articulation. Regular mock rounds refine your STAR method answers and trade-off explanations.",
            "metadata": {
                "category": "interview",
                "platform": "eduoo_ai",
                "action_items": [
                    f"Start an interactive 15-minute mock interview tailored for {role}.",
                    "Review AI feedback on technical accuracy and communication confidence.",
                ],
            },
        },
    )
    generated.append(ins_interview)

    # 5. Consistency Category: Daily Streak & Habit
    ins_consistency, _ = Insight.objects.get_or_create(
        user=user,
        title="Maintain Daily Study Cadence for Accelerated Knowledge Retention",
        defaults={
            "type": "consistency",
            "priority": "medium",
            "message": f"Daily focused study of {user.daily_study_hours or 2} hours yields higher interview retention than sporadic multi-hour weekend sessions.",
            "metadata": {
                "category": "consistency",
                "platform": "eduoo_ai",
                "action_items": [
                    "Complete today's daily task schedule before 9 PM.",
                    "Review previous mock interview mistakes for 10 minutes.",
                ],
            },
        },
    )
    generated.append(ins_consistency)

    # 6. Skills Category: Core Stack & Framework Depth
    ins_skills, _ = Insight.objects.get_or_create(
        user=user,
        title=f"Strengthen Core Framework Ecosystem for {role}",
        defaults={
            "type": "skills",
            "priority": "medium",
            "message": "Modern tech companies test practical framework depth beyond theoretical CS concepts. Ensure you are well-versed in asynchronous operations, database transactions, and test-driven development.",
            "metadata": {
                "category": "skills",
                "platform": "eduoo_ai",
                "action_items": [
                    "Build an end-to-end unit and integration test suite for your main project.",
                    "Review database indexing and query optimization.",
                ],
            },
        },
    )
    generated.append(ins_skills)

    return generated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def insights_list(request):
    queryset = Insight.objects.filter(user=request.user).order_by("-created_at")
    if not queryset.exists():
        _synthesize_user_insights(request.user)
        queryset = Insight.objects.filter(user=request.user).order_by("-created_at")

    category_filter = request.query_params.get("category", "").strip().lower()
    priority_filter = request.query_params.get("priority", "").strip().lower()
    platform_filter = request.query_params.get("platform", "").strip().lower()

    all_data = InsightSerializer(queryset, many=True).data

    # Filter in memory using normalized serializer fields
    filtered = []
    category_counts = {}
    for item in all_data:
        cat = item.get("category", "general").lower()
        category_counts[cat] = category_counts.get(cat, 0) + 1

        if category_filter and category_filter != "all" and cat != category_filter:
            continue
        if priority_filter and priority_filter != "all" and item.get("priority", "").lower() != priority_filter:
            continue
        if platform_filter and platform_filter != "all" and item.get("platform", "").lower() != platform_filter:
            continue
        filtered.append(item)

    return Response({
        "success": True,
        "insights": filtered,
        "total_count": len(all_data),
        "filtered_count": len(filtered),
        "categories": category_counts,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_insights_view(request):
    _synthesize_user_insights(request.user)
    queryset = Insight.objects.filter(user=request.user).order_by("-created_at")
    serializer = InsightSerializer(queryset, many=True)
    return Response({"success": True, "insights": serializer.data})


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def dismiss_insight_view(request, insight_id):
    try:
        insight = Insight.objects.get(id=insight_id, user=request.user)
        insight.delete()
        return Response({"success": True, "message": "Insight dismissed."})
    except Insight.DoesNotExist:
        return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Insight not found."}}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_insight(request):
    serializer = InsightSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    insight = serializer.save(user=request.user)
    return Response({"success": True, "insight": InsightSerializer(insight).data}, status=status.HTTP_201_CREATED)
