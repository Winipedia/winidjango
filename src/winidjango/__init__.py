"""__init__ module."""

import logging

import django
import django_stubs_ext
from django.conf import settings
from pyrig.rig.tools.package_manager import PackageManager

import winidjango
from winidjango.rig.tools.tools import ProjectTester

logger = logging.getLogger(__name__)

django_stubs_ext.monkeypatch()
logger.info("Monkeypatched django-stubs")


logger = logging.getLogger(__name__)


# Configure Django settings for tests if not already configured
if not settings.configured:
    in_this_repo = (PackageManager.I.source_root() / winidjango.__name__).exists()
    if in_this_repo:
        logger.info("Configuring minimal django settings for tests")
        installed_apps = (
            [ProjectTester.I.tests_package_name()]
            if ProjectTester.I.tests_package_root().exists()
            else []
        )
        settings.configure(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=installed_apps,
            USE_TZ=True,
        )
        django.setup()
        logger.info("Django setup complete")
