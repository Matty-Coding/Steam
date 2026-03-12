from django.core.mail import EmailMessage
from .utils import generate_activation_token
from django.conf import settings
from celery import shared_task


@shared_task
def send_activation_email(user) -> bool:
    token_data = generate_activation_token(user)

    uid = token_data.get("uid")
    token = token_data.get("token")

    subject = "Activate your account"

    activation_link = f"http://{settings.FRONTEND_URL}/activate/{uid}/{token}"

    message = f"Please click the link to activate your account: {activation_link}"

    email = EmailMessage(
        subject,
        message,
        to=[user.email],
        from_email=settings.EMAIL_HOST_USER
    )

    if email.send(fail_silently=False):
        return True

    return False
