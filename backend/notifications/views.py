"""Notification views for listing alerts and configuring preferences."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import NotificationPreferenceSerializer, NotificationSerializer
from .services import NotificationService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    unread_only = request.query_params.get("unread") == "true"
    notifications = NotificationService.get_user_notifications(request.user, unread_only=unread_only)
    return Response({"success": True, "notifications": NotificationSerializer(notifications, many=True).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request):
    notif_id = request.data.get("id")
    NotificationService.mark_as_read(request.user, notification_id=notif_id)
    return Response({"success": True, "message": "Notifications updated."})


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def notification_preferences_view(request):
    if request.method == "PUT":
        prefs = NotificationService.update_preferences(request.user, request.data)
        return Response({"success": True, "preferences": NotificationPreferenceSerializer(prefs).data})

    prefs = NotificationService.get_or_create_preferences(request.user)
    return Response({"success": True, "preferences": NotificationPreferenceSerializer(prefs).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def notification_test_email_view(request):
    target_email = request.data.get("email")
    try:
        result = NotificationService.send_test_email(request.user, target_email=target_email)
        if result.get("success"):
            return Response({
                "success": True,
                "message": result.get("message", "Test email dispatched successfully!"),
                "recipient": result.get("recipient"),
            })
        return Response(
            {
                "success": False,
                "error": {
                    "code": "EMAIL_DISPATCH_FAILED",
                    "message": result.get("error", "Failed to dispatch email."),
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as exc:
        return Response(
            {
                "success": False,
                "error": {"code": "EMAIL_ERROR", "message": str(exc)},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
