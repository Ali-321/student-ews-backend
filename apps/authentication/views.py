from core.permissions import IsAdminRole
from django.shortcuts import render
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .selectors import user_get_me_selector, user_list_selector
from .serializers import (
    AuthTokenDataOutputSerializer,
    LoginInputSerializer,
    TokenRefreshDataOutputSerializer,
    TokenRefreshInputSerializer,
    UserCreateInputSerializer,
    UserListOutputSerializer,
    UserMeOutputSerializer,
)
from .services import auth_login_service, user_create_service


class UserListCreateApi(APIView):
  permission_classes = [IsAdminRole]

  @extend_schema(
      summary="Ambil Daftar User",
      description="Mengambil daftar seluruh akun user dengan filter role.",
      parameters=[
          OpenApiParameter(
              name="role",
              type=OpenApiTypes.STR,
              location=OpenApiParameter.QUERY,
              description="Filter berdasarkan role user (contoh: ADMIN, TEACER)",
              required=False,
          )
      ],
      responses={
          200: inline_serializer(
              name="UserListResponse",
              fields={
                  "success": serializers.BooleanField(default=True),
                  "message": serializers.CharField(
                      default="Daftar user berhasil diambil."
                  ),
                  "data": UserListOutputSerializer(many=True),
              },
          )
      },
  )
  def get(self, request):
    role_filter = request.query_params.get("role")
    users = user_list_selector(role=role_filter)
    serializer = UserListOutputSerializer(users, many=True)
    return Response(
        {
            "success": True,
            "message": "Daftar user berhasil diambil.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )

  @extend_schema(
      summary="Buat Akun User Baru",
      description="Membuat akun user baru dalam sistem (Membutuhkan akses Admin).",
      request=UserCreateInputSerializer,
      responses={
          201: inline_serializer(
              name="UserCreateResponse",
              fields={
                  "success": serializers.BooleanField(default=True),
                  "message": serializers.CharField(
                      default="Akun berhasil dibuat."
                  ),
                  "data": UserListOutputSerializer(),
              },
          )
      },
  )
  def post(self, request):
    serializer = UserCreateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = user_create_service(**serializer.validated_data)
    output_serializer = UserListOutputSerializer(user)

    return Response(
        {
            "success": True,
            "message": "Akun berhasil dibuat.",
            "data": output_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


class LoginApi(APIView):
  permission_classes = []

  @extend_schema(
      summary="Login User",
      description="Autentikasi email & password untuk mendapatkan pasangan JWT Access & Refresh token.",
      request=LoginInputSerializer,
      responses={
          200: inline_serializer(
              name="LoginSuccessResponse",
              fields={
                  "success": serializers.BooleanField(default=True),
                  "message": serializers.CharField(default="Login berhasil."),
                  "data": AuthTokenDataOutputSerializer(),
              },
          ),
          400: inline_serializer(
              name="LoginValidationErrorResponse",
              fields={
                  "email": serializers.ListField(
                      child=serializers.CharField()
                  ),
                  "password": serializers.ListField(
                      child=serializers.CharField()
                  ),
              },
          ),
      },
  )
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
  permission_classes = []

  @extend_schema(
      summary="Refresh Access Token JWT",
      description="Memperbarui access token yang kadaluwarsa dengan mengirimkan refresh token yang valid.",
      request=TokenRefreshInputSerializer,
      responses={
          200: inline_serializer(
              name="TokenRefreshSuccessResponse",
              fields={
                  "success": serializers.BooleanField(default=True),
                  "message": serializers.CharField(
                      default="Token berhasil diperbarui."
                  ),
                  "data": TokenRefreshDataOutputSerializer(),
              },
          ),
          401: inline_serializer(
              name="TokenRefreshErrorResponse",
              fields={
                  "success": serializers.BooleanField(default=False),
                  "message": serializers.CharField(
                      default="Token tidak valid atau sudah kadaluwarsa."
                  ),
              },
          ),
      },
  )
  def post(self, request):
    serializer = TokenRefreshInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
      refresh = RefreshToken(serializer.validated_data["refresh"])
      data = {
          "access_token": str(refresh.access_token),
      }
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
  permission_classes = [IsAuthenticated]

  @extend_schema(
      summary="Ambil Profil User Aktif",
      description="Mengambil detail profil akun user yang sedang aktif berdasarkan Bearer Token.",
      responses={
          200: inline_serializer(
              name="UserMeResponse",
              fields={
                  "success": serializers.BooleanField(default=True),
                  "message": serializers.CharField(
                      default="Profil berhasil diambil."
                  ),
                  "data": UserMeOutputSerializer(),
              },
          )
      },
  )
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