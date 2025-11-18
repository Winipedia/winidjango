"""__init__ module."""

import logging

import winidjango

logger = logging.getLogger(__name__)

logger.info(
    "Imported django: %s to setup django in tests for winiutils.django",
    winidjango,
)
