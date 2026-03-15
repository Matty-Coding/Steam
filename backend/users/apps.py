from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"

    # register signals
    def ready(self):
        import users.signals
