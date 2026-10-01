from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.forms"
    label = "forms"

    def ready(self):
        from apps.forms import signals  # noqa: F401
        from apps.forms.fields import handlers  # noqa: F401
