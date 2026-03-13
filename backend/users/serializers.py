from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status


class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password", "confirm_password")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True}
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Password do not match"
            })

        try:
            user = CustomUser(email=attrs["email"])
            validate_password(attrs["password"], user)

        except ValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        try:
            user = CustomUser.objects.create_user(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "email": "Email already registered"
            })

        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed({
                "message": "Account not activated"
            }, status=status.HTTP_401_UNAUTHORIZED)

        attrs["user"] = user

        return attrs
