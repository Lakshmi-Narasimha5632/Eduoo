from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PLATFORM_CHOICES, ConnectedPlatform
from .services import PlatformService


SUPPORTED_PLATFORMS = [code for code, _ in PLATFORM_CHOICES]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def platform_list(request):
    platforms = []
    unified = PlatformService.get_unified_analytics(request.user)
    p_map = unified.get("platforms", {})

    for platform_code, platform_name in PLATFORM_CHOICES:
        obj, _ = ConnectedPlatform.objects.get_or_create(user=request.user, platform=platform_code)
        plat_data = p_map.get(platform_code, {})
        platforms.append(
            {
                "platform": platform_code,
                "display_name": platform_name,
                "connected": obj.connected,
                "username": obj.username,
                "last_synced_at": obj.last_synced_at,
                "sync_status": obj.sync_status,
                "sync_error": obj.sync_error,
                "raw_data": plat_data.get("analytics") or {},
                "profile": plat_data.get("profile") or {},
            }
        )

    return Response({"success": True, "platforms": platforms})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def connect_platform(request, platform):
    if platform not in SUPPORTED_PLATFORMS:
        return Response(
            {"success": False, "error": {"code": "INVALID_PLATFORM", "message": "Unsupported platform."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    username = request.data.get("username")
    access_token = request.data.get("access_token")
    refresh_token = request.data.get("refresh_token")

    platform_record, _ = ConnectedPlatform.objects.get_or_create(user=request.user, platform=platform)
    platform_record.username = username or platform_record.username
    platform_record.connected = True
    platform_record.sync_status = "syncing"
    platform_record.sync_error = None

    if access_token:
        platform_record.set_access_token(access_token)
    if refresh_token:
        platform_record.set_refresh_token(refresh_token)

    platform_record.save()

    # Automatically trigger sync upon connect
    try:
        sync_payload = PlatformService.sync_platform(
            platform,
            username=platform_record.username,
            access_token=platform_record.get_access_token(),
            refresh_token=platform_record.get_refresh_token(),
            user=request.user,
        )
        platform_record.refresh_from_db()
        platform_record.sync_status = "success"
        platform_record.last_synced_at = sync_payload.get("last_synced_at") or platform_record.last_synced_at
        platform_record.save(update_fields=["sync_status", "last_synced_at", "updated_at"])
    except Exception as e:
        platform_record.sync_status = "error"
        platform_record.sync_error = str(e)
        platform_record.save(update_fields=["sync_status", "sync_error", "updated_at"])

    return Response(
        {
            "success": True,
            "platform": platform,
            "connected": platform_record.connected,
            "username": platform_record.username,
            "last_synced_at": platform_record.last_synced_at,
            "sync_status": platform_record.sync_status,
            "sync_error": platform_record.sync_error,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_platform(request, platform):
    if platform not in SUPPORTED_PLATFORMS:
        return Response(
            {"success": False, "error": {"code": "INVALID_PLATFORM", "message": "Unsupported platform."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    platform_record = get_object_or_404(ConnectedPlatform, user=request.user, platform=platform)
    platform_record.sync_status = "syncing"
    platform_record.save(update_fields=["sync_status", "updated_at"])

    sync_payload = PlatformService.sync_platform(
        platform,
        username=platform_record.username,
        access_token=platform_record.get_access_token(),
        refresh_token=platform_record.get_refresh_token(),
        user=request.user,
    )

    platform_record.sync_status = "success"
    platform_record.sync_error = None
    platform_record.last_synced_at = sync_payload.get("last_synced_at") or platform_record.last_synced_at
    platform_record.connected = bool(sync_payload.get("connected", platform_record.connected))
    platform_record.save(update_fields=["sync_status", "sync_error", "last_synced_at", "connected", "updated_at"])

    return Response({"success": True, "platform": platform, "connected": platform_record.connected, "sync_status": "success", "payload": sync_payload})


@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def disconnect_platform(request, platform):
    if platform not in SUPPORTED_PLATFORMS:
        return Response(
            {"success": False, "error": {"code": "INVALID_PLATFORM", "message": "Unsupported platform."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    platform_record = get_object_or_404(ConnectedPlatform, user=request.user, platform=platform)
    platform_record.connected = False
    platform_record.username = None
    platform_record.access_token = None
    platform_record.refresh_token = None
    platform_record.token_expiry = None
    platform_record.sync_status = "disconnected"
    platform_record.sync_error = None
    platform_record.cached_analytics = {}
    platform_record.save()

    return Response({"success": True, "platform": platform, "connected": False})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unified_analytics_view(request):
    """Section 11 unified analytics endpoint."""
    analytics = PlatformService.get_unified_analytics(request.user)
    return Response({"success": True, "analytics": analytics, **analytics})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leetcode_catalog_view(request):
    """Section 5 LeetCode problem catalog endpoint."""
    from .models import LeetCodeCatalogProblem
    from .services import PlatformService

    # Ensure catalog is populated
    if not LeetCodeCatalogProblem.objects.exists():
        PlatformService._sync_leetcode_problems(request.user, {})

    difficulty = request.query_params.get("difficulty")
    qs = LeetCodeCatalogProblem.objects.all()
    if difficulty:
        qs = qs.filter(difficulty__iexact=difficulty)

    problems = [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,
            "topics": p.topics,
            "problem_url": p.problem_url,
            "external_id": p.external_id,
        }
        for p in qs
    ]
    return Response({"success": True, "count": len(problems), "problems": problems})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def linkedin_auth_url_view(request):
    """Section 8 LinkedIn OAuth Authorization URL."""
    from .connectors.linkedin import LinkedInConnector
    state = f"user_{request.user.id}"
    auth_url = LinkedInConnector.get_authorization_url(state=state)
    return Response({"success": True, "authorization_url": auth_url})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def linkedin_callback_view(request):
    """Section 8 LinkedIn OAuth Callback / Token Exchange."""
    from .connectors.linkedin import LinkedInConnector
    code = request.data.get("code")
    if not code:
        return Response(
            {"success": False, "error": {"code": "MISSING_CODE", "message": "Authorization code is required."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_data = LinkedInConnector.exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        return Response(
            {"success": False, "error": {"code": "OAUTH_FAILED", "message": "Failed to exchange code for access token."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    platform_record, _ = ConnectedPlatform.objects.get_or_create(user=request.user, platform="linkedin")
    platform_record.set_access_token(access_token)
    platform_record.connected = True
    platform_record.sync_status = "connected"
    platform_record.save()

    # Sync profile info immediately
    sync_payload = PlatformService.sync_platform(
        "linkedin",
        access_token=access_token,
        user=request.user,
    )
    return Response({"success": True, "platform": "linkedin", "connected": True, "payload": sync_payload})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_all_platforms_view(request):
    """Section 11 Sync All Platforms."""
    connected_records = ConnectedPlatform.objects.filter(user=request.user, connected=True)
    synced = []
    for record in connected_records:
        try:
            PlatformService.sync_platform(
                record.platform,
                username=record.username,
                access_token=record.get_access_token(),
                refresh_token=record.get_refresh_token(),
                user=request.user,
            )
            synced.append(record.platform)
        except Exception:
            pass
    return Response({"success": True, "synced_platforms": synced})

