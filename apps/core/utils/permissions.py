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


class IsGuruRole(BasePermission):
    """Permission khusus: Hanya Superuser atau Role Guru dan admin yang diizinkan."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == User.Role.GURU or request.user.role == User.Role.ADMIN)
        )

class IsOrangTuaRole(BasePermission):
    """Permission khusus: Hanya Superuser atau Role Orang Tua yang diizinkan."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == User.Role.ORANGTUA or request.user.role == User.Role.ADMIN)
        )

class IsSiswaRole(BasePermission):
    """Permission khusus: Hanya Superuser atau Role Siswa yang diizinkan."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == User.Role.SISWA or request.user.role == User.Role.ADMIN)
        )