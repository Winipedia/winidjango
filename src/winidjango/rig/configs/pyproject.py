"""Manage pyproject.toml (PEP 518, 621, 660).

Handles metadata, dependencies, build config (uv), tool configs (ruff, ty, pytest,
bandit, rumdl). Enforces opinionated defaults: all ruff rules (except D203, D213,
COM812, ANN401), Google docstrings, strict ty, bandit security, coverage threshold.
Validation uses subset checking (users can add extra configs). Priority 20 (created
early for other configs to read).

Utility methods: project info, dependencies, Python versions, license detection,
classifiers.
"""

from typing import Any

from pyrig.rig.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile


class PyprojectConfigFile(BasePyprojectConfigFile):
    """You can override methods from the base class to customize behavior."""

    def _configs(self) -> dict[str, Any]:
        configs = super()._configs()

        # add exclude = ["**/migrations/*.py",]
        exclude = (
            configs.setdefault("tool", {})
            .setdefault("ruff", {})
            .setdefault("exclude", [])
        )
        exclude.append("**/migrations/*.py")
        return configs
