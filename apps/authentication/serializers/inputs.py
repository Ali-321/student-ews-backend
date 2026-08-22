from rest_framework import serializers

from authentication.models import User

class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenRefreshInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class UserCreateInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)