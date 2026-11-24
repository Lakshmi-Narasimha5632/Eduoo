"""Permission classes for Eduoo."""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Ensure that only the owner of an object can access or modify it."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "plan") and hasattr(obj.plan, "user"):
            return obj.plan.user == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False
