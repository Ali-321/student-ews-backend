from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .selectors import user_get_me_selector
from .serializers import (LoginInputSerializer,TokenRefreshInputSerializer,UserMeOutputSerializer,)
from .services import auth_login_service


class LoginApi(APIView):
    # Public endpoint (tidak perlu token untuk login)
    permission_classes = []

    def post(self, request):
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = auth_login_service(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "success": True,
                "message": "Login berhasil.",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )
class TokenRefreshApi(APIView):
    # Public endpoint
    permission_classes = []

    def post(self, request):
        serializer = TokenRefreshInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            data = {
                "access_token": str(refresh.access_token),
            }
            # Jika opsi ROTATE_REFRESH_TOKENS aktif
            if getattr(refresh, "token", None):
                data["refresh_token"] = str(refresh)
        except (TokenError, InvalidToken):
            return Response(
                {
                    "success": False,
                    "message": "Token tidak valid atau sudah kadaluwarsa.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "success": True,
                "message": "Token berhasil diperbarui.",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class MeApi(APIView):
    # Hanya bisa diakses oleh user yang membawa Authorization Header (Bearer token)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = user_get_me_selector(user=request.user)
        serializer = UserMeOutputSerializer(user)

        return Response(
            {
                "success": True,
                "message": "Profil berhasil diambil.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )