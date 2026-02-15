"""Override pyrig tools."""

from pyrig.rig.tools.project_tester import ProjectTester as BaseProjectTester
from winiutils.rig.tools.pyrigger import Pyrigger as BasePyrigger


class Pyrigger(BasePyrigger):
    """Subclass of Pyrigger for customizing pyrig behavior."""

    def dev_dependencies(self) -> list[str]:
        """Get the dev dependencies."""
        return [*super().dev_dependencies(), "django-stubs"]


class ProjectTester(BaseProjectTester):
    """Subclass of ProjectTester for customizing pyrig behavior."""

    def dev_dependencies(self) -> list[str]:
        """Get the dev dependencies."""
        return [*super().dev_dependencies(), "pytest-django"]
