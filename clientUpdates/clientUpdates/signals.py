from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging

logger = logging.getLogger('clientUpdates')


@receiver(user_logged_in)
def log_user_login(sender, request, **kwargs):
    logger.info(f"{request.user.username} has logged in.")


@receiver(user_logged_out)
def log_user_logout(sender, request, **kwargs):
    logger.info(f"{request.user.username} has logged out.")
