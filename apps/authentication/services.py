from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


def auth_login_service(*, email: str, password: str) -> dict:
    """Service untuk mencocokkan kredensial user dan menerbitkan JWT token."""
    user = authenticate(username=email, password=password)

    if not user:
        raise AuthenticationFailed("Email atau password salah.")

    if not user.is_active:
        raise AuthenticationFailed("Akun Anda sedang tidak aktif.")

    # Generate Token JWT
    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_superuser": user.is_superuser,
        },
    }