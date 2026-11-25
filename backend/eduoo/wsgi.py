"""
WSGI config for eduoo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduoo.settings')

application = get_wsgi_application()

# Automatically run pending database migrations on application boot
try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
except Exception as exc:
    logging.getLogger(__name__).warning("WSGI auto-migration notice: %s", exc)
