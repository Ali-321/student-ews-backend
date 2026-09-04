from rest_framework import serializers
from authentication.models import User


class UserMeOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "is_superuser", "is_staff", "date_joined")


class UserListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "is_active", "date_joined")

# --- Schema Output Khusus Autentikasi ---
class AuthTokenDataOutputSerializer(serializers.Serializer):
  access_token = serializers.CharField()
  refresh_token = serializers.CharField(required=False)
  user = UserMeOutputSerializer(required=False)


class TokenRefreshDataOutputSerializer(serializers.Serializer):
  access_token = serializers.CharField()
  refresh_token = serializers.CharField(required=False)