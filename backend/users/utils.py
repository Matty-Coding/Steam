from django.core import signing
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import CustomUser
from django.conf import settings


def generate_activation_token(user: CustomUser) -> dict[str, str]:
    # token with salt, token_value (positive integer)
    # timestamp, signed by secret key
    token = signing.dumps(
        user.token_value, salt=settings.SALT_ACTIVATION_ACCOUNT
    )

    return {
        "token": token,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
    }


def validate_activation_token(uidb64, token) -> CustomUser | None:
    try:
        # decode user id from base64 to string
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)  # get user object

        # extracting token_value from full token
        extracted_token = signing.loads(
            token,
            salt=settings.SALT_ACTIVATION_ACCOUNT,
            max_age=settings.TOKEN_MAX_AGE  # expiration
        )

        # check if token is valid
        if extracted_token == user.token_value:
            return user

    except (
        CustomUser.DoesNotExist,   # user does not exist
        signing.BadSignature,      # invalid token
        signing.SignatureExpired   # token expired
    ):

        return None


def generate_reset_token(user: CustomUser) -> dict[str, str]:
    # token with salt, token_value (positive integer)
    # timestamp, signed by secret key
    token = signing.dumps(
        user.token_value, salt=settings.SALT_RESET_PASSWORD)

    return {
        "token": token,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
    }


def validate_reset_token(uidb64, token) -> CustomUser | None:
    try:
        # decode user id from base64 to string
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)  # get user object

        # extracting token_value from full token
        extracted_token = signing.loads(
            token,
            salt=settings.SALT_RESET_PASSWORD,
            max_age=settings.TOKEN_MAX_AGE   # expiration
        )

        # check if token is valid
        if extracted_token == user.token_value:
            return user

    except (
        CustomUser.DoesNotExist,   # user does not exist
        signing.BadSignature,      # invalid token
        signing.SignatureExpired   # token expired
    ):

        return None
