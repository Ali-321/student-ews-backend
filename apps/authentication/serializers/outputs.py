from rest_framework import serializers
from authentication.models import User


class UserMeOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "is_superuser", "is_staff", "date_joined")