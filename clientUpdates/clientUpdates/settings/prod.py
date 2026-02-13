
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

## OLD: DO blocked SMTP ports 465, 587 on Oct, 2025, so this does not work anymore
EMAIL_BACKEND = 'clientUpdates.custom_smtp_backend.CustomEmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '').split(',')

# EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
# ANYMAIL = { "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY") }
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
# SERVER_EMAIL = DEFAULT_FROM_EMAIL
# EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")

MIDDLEWARE += ['clientUpdates.middleware.DebugHeadersMiddleware']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname}; {asctime}; logger name: {name}; module: {module}; msg: {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'production.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'clientUpdates': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}


