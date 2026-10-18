"""__init__ module."""

import logging
import sys
from pathlib import Path

import django
import django_stubs_ext
from django.conf import settings
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
        if ProjectTester.I.package_root().exists():
            sys.path.insert(0, str(ProjectTester.I.source_root()))
            installed_apps = [ProjectTester.I.package_name()]
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
