from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        # Import signals when apps are ready (safe point).
        from . import signals  # noqa: F401
