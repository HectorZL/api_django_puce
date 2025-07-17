from django.apps import AppConfig


class MenusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.menus'
    verbose_name = 'Gestión de Menús y Pedidos'
    
    def ready(self):
        # Import and register signals
        import apps.menus.signals  # noqa
