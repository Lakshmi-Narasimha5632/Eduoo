"""Account permission classes."""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to the account owner or superusers."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj == request.user or (hasattr(obj, "user") and obj.user == request.user)
