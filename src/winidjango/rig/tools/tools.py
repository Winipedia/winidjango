"""Override pyrig tools."""

from typing import override

from pyrig.rig.tools.testing.project import ProjectTester as BaseProjectTester


class ProjectTester(BaseProjectTester):
    """Subclass of ProjectTester for customizing pyrig behavior."""

    @override
    def dev_dependencies(self) -> tuple[str, ...]:
        """Get the dev dependencies."""
        return (*super().dev_dependencies(), "pytest-django")
