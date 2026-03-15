from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)  # intercept user creation
def create_profile(sender, instance, created, **kwargs):

    if not created:
        return

    # create profile with username based on email
    if instance.is_superuser and instance.is_staff:
        username = f"admin-{instance.email.split('@')[0]}"

    else:
        username = instance.email.split("@")[0]

    Profile.objects.create(
        user=instance,
        username=username
    )
