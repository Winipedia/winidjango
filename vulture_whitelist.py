"""Explicit references for reviewed dead code false positives."""

from typing import Self

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.management import BaseCommand
from django.db.models import Field
from django.db.models.fields.related import ForeignObjectRel

from winidjango.core.commands.base.base import ABCBaseCommand
from winidjango.core.commands.import_data import ImportDataBaseCommand
from winidjango.core.db import bulk, setup, sql
from winidjango.core.db.models import BaseModel
from winidjango.rig.configs.pyproject import DjangoPyprojectConfigFile

_COMMAND_OVERRIDES = (
    ABCBaseCommand.get_option,
    BaseCommand.add_arguments,
    BaseCommand.handle,
)
_COMMANDS = (ImportDataBaseCommand,)
_CONFIG_FILES = (DjangoPyprojectConfigFile,)
_DJANGO_MODEL_PROTOCOL = (
    Field,
    ForeignObjectRel,
    Self,
)
_DJANGO_MODELS = (
    BaseModel,
    BaseModel.created_at,
    BaseModel.Meta,
    BaseModel.meta,
    BaseModel.Meta.abstract,
    BaseModel.updated_at,
)
_DJANGO_TYPE_CHECKING = (GenericForeignKey,)
_PUBLIC_HELPERS = (
    bulk.bulk_delete_in_steps,
    bulk.bulk_update_in_steps,
    bulk.get_differences_between_bulks,
    bulk.multi_simulate_bulk_deletion,
    setup.migrate_safely,
    sql.execute_sql,
)
