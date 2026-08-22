from rest_framework.permissions import BasePermission
from authentication.models import User


class IsAdminRole(BasePermission):
    """Permission khusus: Hanya Superuser atau Role Admin yang diizinkan."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == User.Role.ADMIN)
        )