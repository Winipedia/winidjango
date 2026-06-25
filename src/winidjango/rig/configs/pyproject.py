"""Manage pyproject.toml (PEP 518, 621, 660).

Handles metadata, dependencies, build config (uv), tool configs (ruff, ty, pytest,
bandit, rumdl). Enforces opinionated defaults: all ruff rules (except D203, D213,
COM812, ANN401), Google docstrings, strict ty, bandit security, coverage threshold.
Validation uses subset checking (users can add extra configs). Priority 20 (created
early for other configs to read).

Utility methods: project info, dependencies, Python versions, license detection,
classifiers.
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.pyproject import (  # deptry: ignore[DEP004]
    PyprojectConfigFile as BasePyprojectConfigFile,
)
from pyrig_runtime.core.strings import snake_to_kebab_case

import winidjango


class PyprojectConfigFile(BasePyprojectConfigFile):
    """You can override methods from the base class to customize behavior."""

    def _configs(self) -> dict[str, Any]:
        configs = super()._configs()

        configs["tool"]["ruff"].setdefault("exclude", []).extend(["**/migrations/*.py"])
        return configs


if Path.cwd().name == snake_to_kebab_case(winidjango.__name__):
    from pyrig_pypi.rig.configs.pyproject import (  # deptry: ignore[DEP004]
        PyprojectConfigFile as PyPIPyprojectConfigFile,
    )

    class DjangoPyprojectConfigFile(PyPIPyprojectConfigFile, PyprojectConfigFile):
        """Overrides base to resolve conflicts.

        Only needed when developing Winidjango itself.
        """
