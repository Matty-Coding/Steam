from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import CustomUser


def generate_activation_token(user):
    return {
        "token": default_token_generator.make_token(user),
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
    }


def validate_activation_token(uid, token):

    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return None

    if default_token_generator.check_token(user, token):
        return user

    return None
