"""__init__ module."""

import logging
from pathlib import Path

import django
import django_stubs_ext
from django.conf import settings
from pyrig.core.introspection.modules import import_module_with_file_fallback
from pyrig_runtime.core.strings import snake_to_kebab_case

import winidjango
from winidjango.rig.tools.tools import ProjectTester

logger = logging.getLogger(__name__)

django_stubs_ext.monkeypatch()
logger.info("Monkeypatched django-stubs")


logger = logging.getLogger(__name__)


# Configure Django settings for tests if not already configured
if not settings.configured:
    in_this_repo = Path.cwd().name == snake_to_kebab_case(winidjango.__name__)
    if in_this_repo:
        logger.info("Configuring minimal django settings for tests")
        # manual import needed bc tests is not a registered package
        if ProjectTester.I.package_root().exists():
            tests_package = import_module_with_file_fallback(
                path=ProjectTester.I.package_root(),
                name=ProjectTester.I.package_name(),
            )
            installed_apps = [tests_package.__name__]
        else:
            installed_apps = []
        settings.configure(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                },
            },
            INSTALLED_APPS=installed_apps,
            USE_TZ=True,
        )
        django.setup()
        logger.info("Django setup complete")
