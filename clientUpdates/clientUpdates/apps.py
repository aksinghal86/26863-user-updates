from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in, user_logged_out


class MyAppConfig(AppConfig):

    name = 'clientUpdates'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
