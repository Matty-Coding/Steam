from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):

        # email field required
        if not email:
            raise ValueError("The Email field must be set")

        # normalization to lower
        email = self.normalize_email(email)

        # registration
        user = self.model(email=email, **extra_fields)

        # auto hashing by django default
        user.set_password(password)

        # if not superuser, set account as inactive
        user.is_active = False

        # save using current database instance
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        # set default values for superuser
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):

    # username field is not required
    username = None

    # optional fields removed
    first_name = None
    last_name = None

    # email field unique and indexing to improve query performance
    email = models.EmailField(unique=True, db_index=True, null=False)
    password = models.CharField(null=False, max_length=255)

    # special field to generate and alter activation token
    token_value = models.PositiveIntegerField(default=1)

    # switching username field to email
    USERNAME_FIELD = "email"

    # no more required fields
    REQUIRED_FIELDS = []

    # load custom user manager into custom user
    objects = CustomUserManager()

    # verbose readable names for admin panel
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    # representation of model
    def __repr__(self):
        return self.email


class Profile(models.Model):

    # one to one relationship with custom user + cascade delete
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # username custom field
    username = models.CharField(max_length=50, null=True)
    icon = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __repr__(self):
        return self.username
