from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """Права доступа для автора и администратора."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return any((
            request.method in permissions.SAFE_METHODS,
            obj.author == request.user,
            request.user.is_staff,
            request.user.is_superuser,
        ))
