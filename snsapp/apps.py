from django.apps import AppConfig


class SnsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'snsapp'

    def ready(self):#要確認
        from .ap_scheduler import start
        start()
