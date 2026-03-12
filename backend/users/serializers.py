from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password", "confirm_password")

        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):

        if CustomUser.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError("Email already exists")

        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match")

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "password")

        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):

        if not CustomUser.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError("User does not exist")

        return attrs
