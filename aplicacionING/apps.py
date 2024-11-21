from django.apps import AppConfig

class AplicacioningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicacionING'

    def ready(self):
        # Importa las señales para asegurarte de que se registren
        import aplicacionING.signals
