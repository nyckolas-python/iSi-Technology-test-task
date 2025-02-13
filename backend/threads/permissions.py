from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsParticipant(permissions.BasePermission):
    """Allow access only to thread participants or admins"""

    def has_permission(self, request, view):
        user_id = view.kwargs.get("user_id")
        return request.user and (request.user.id == user_id or request.user.is_staff)
