from rest_framework import serializers

class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenRefreshInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)