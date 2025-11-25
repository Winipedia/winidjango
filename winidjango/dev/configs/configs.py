"""Configs for pyrig.

All subclasses of ConfigFile in the configs package are automatically called.
"""

from pyrig.dev.configs.pyproject import PyprojectConfigFile as PyrigPyprojectConfigFile


class PyprojectConfigFile(PyrigPyprojectConfigFile):
    """Pyproject.toml config file."""

    @classmethod
    def get_standard_dev_dependencies(cls) -> dict[str, str | dict[str, str]]:
        """Get the standard dev dependencies."""
        dev_dependencies = super().get_standard_dev_dependencies()
        dev_dependencies["django-stubs"] = "*"
        dev_dependencies["pytest-django"] = "*"

        return dict(sorted(dev_dependencies.items()))
