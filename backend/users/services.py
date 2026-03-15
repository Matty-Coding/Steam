from django.core.mail import EmailMessage
from .utils import generate_activation_token
from django.conf import settings


def send_activation_email(user):
    token_data = generate_activation_token(user)

    token = token_data.get("token")

    subject = "Activate your account"

    activation_link = f"{settings.FRONTEND_URL}/auth/activate/{token}"

    message = f"Please click the link to activate your account: {activation_link}"

    email = EmailMessage(
        subject,
        message,
        to=[user.email],
        from_email=settings.EMAIL_HOST_USER
    )

    try:
        sent = email.send(fail_silently=False)
        return sent == 1

    except:
        return False
