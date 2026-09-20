from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from authentication.models import User


def auth_login_service(*, email: str, password: str) -> dict:
    """Service untuk mencocokkan kredensial user dan menerbitkan JWT token."""
    
    user = User.objects.filter(email=email).first()

    if not user or not user.check_password(password):
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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
        },
    }

def user_create_service(*, email: str, password: str, role: str, first_name: str = "", last_name: str = "") -> User:
    """Service mutasi untuk membuat user baru oleh Admin."""
    if User.objects.filter(email=email).exists():
        raise ValidationError({"email": "User dengan email ini sudah terdaftar."})
    
    if role in User.Role.SUPERUSER:
        raise ValidationError({"role": "Role ini tidak dapat digunakan untuk membuat user baru."})
    
    user = User.objects.create_user(
        email=email,
        password=password,
        role=role,
        first_name=first_name,
        last_name=last_name,
    )
    return user