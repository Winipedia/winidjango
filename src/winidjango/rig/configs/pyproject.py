"""Manage pyproject.toml (PEP 518, 621, 660).

Handles metadata, dependencies, build config (uv), tool configs (ruff, ty, pytest,
bandit, rumdl). Enforces opinionated defaults: all ruff rules (except D203, D213,
COM812, ANN401), Google docstrings, strict ty, bandit security, coverage threshold.
Validation uses subset checking (users can add extra configs). Priority 20 (created
early for other configs to read).

Utility methods: project info, dependencies, Python versions, license detection,
classifiers.
"""

from pyrig.core.introspection.packages import is_src_package
from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.pyproject import (
    PyprojectConfigFile as BasePyprojectConfigFile,
)

import winidjango


class PyprojectConfigFile(BasePyprojectConfigFile):
    """You can override methods from the base class to customize behavior."""

    def _configs(self) -> ConfigDict:
        configs = super()._configs()

        configs["tool"]["ruff"].setdefault("exclude", []).extend(["**/migrations/*.py"])
        return configs


if is_src_package(winidjango):
    from pyrig_pypi.rig.configs.pyproject import (
        PyprojectConfigFile as PyPIPyprojectConfigFile,
    )

    class DjangoPyprojectConfigFile(PyPIPyprojectConfigFile, PyprojectConfigFile):
        """Overrides base to resolve conflicts.

        Only needed when developing Winidjango itself.
        """
