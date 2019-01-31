import os
import django
from channels.routing import get_default_application

"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
application = get_default_application()
