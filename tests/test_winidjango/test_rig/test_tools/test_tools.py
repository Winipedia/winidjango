"""module."""

from winidjango.rig.tools.tools import ProjectTester


class TestProjectTester:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ProjectTester().dev_dependencies()
        assert "pytest-django" in result
