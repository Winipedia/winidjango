"""__init__ module."""

import logging

import django
import django_stubs_ext
from django.conf import settings

logger = logging.getLogger(__name__)

django_stubs_ext.monkeypatch()
logger.info("Monkeypatched django-stubs")

if not settings.configured:
    logger.info("Configuring minimal django settings")
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=["tests"],
    )
    django.setup()
