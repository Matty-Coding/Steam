from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status

# Register Serializer with ModelSerializer class


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (ModelSerializer)

    Confirm password is required
    """

    # adding custom field to serializer for password
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        # associate model
        model = CustomUser

        # required fields
        fields = ("email", "password", "confirm_password")

        # additional settings
        extra_kwargs = {
            # password is write only (no returning it)
            "password": {"write_only": True},
            "email": {"required": True}         # email is required
        }

    # override validate method
    def validate(self, attrs) -> dict[str, str]:

        # check matching password
        if attrs["password"] != attrs["confirm_password"]:

            # throw serializer error with custom message
            raise serializers.ValidationError({
                "confirm_password": "Password do not match"
            })

        try:
            user = CustomUser(email=attrs["email"])

            # validate password
            validate_password(attrs["password"], user)

        # catch validation error
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        # return validated data
        return attrs

    # override create method
    def create(self, validated_data):

        # remove confirm password (custom field)
        validated_data.pop("confirm_password")

        try:
            # create user using custom create_user override
            user = CustomUser.objects.create_user(**validated_data)

        # catch integrity error
        # django db exception
        except IntegrityError:
            raise serializers.ValidationError({
                "email": "Email already registered"
            })

        # return user object
        return user


# Login Serializer with Serializer class
# login does not require to reflect model
# just checking credentials
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login (Serializer)

    Only email and password are required
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        # get email and password from request data
        email = attrs.get("email")
        password = attrs.get("password")

        # check if user exists
        user = CustomUser.objects.filter(email=email).first()

        if not user or not user.check_password(password):

            # throw authentication error (DRF exception)
            raise AuthenticationFailed({
                "message": "Invalid credentials"
            }, code=status.HTTP_401_UNAUTHORIZED)

        # check if account is active
        # custom logic for account activation
        # manage it with resend activation link
        if not user.is_active:
            raise AuthenticationFailed({
                "message": "Account not activated",
                "userEmail": user.email
            }, code=status.HTTP_401_UNAUTHORIZED)

        # add user object to validated data
        attrs["user"] = user

        # return validated data
        return attrs
