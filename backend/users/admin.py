from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


# Register your models here.


class CustomUserAdmin(UserAdmin):

    model = CustomUser

    ordering = ("email",)

    list_display = ("email", "is_staff", "is_active")

    fieldsets = (
        (
            "Credentials",
            {
                "classes": ("wide",),
                "fields": ("email", "password"),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    add_fieldsets = (
        ("Credentials", {"classes": ("wide",),
         "fields": ("email", "password")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
