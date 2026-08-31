from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import os

        if os.environ.get("RUN_MAIN") == "true":
            try:
                from django.contrib.auth.models import User

                username = "Admin"
                password = "Admin@#123"

                user, created = User.objects.get_or_create(
                    username=username
                )

                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.save()

            except Exception:
                pass