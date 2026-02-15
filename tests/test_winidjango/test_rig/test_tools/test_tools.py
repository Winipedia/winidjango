"""module."""

from winidjango.rig.tools.tools import ProjectTester, Pyrigger


class TestPyrigger:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = Pyrigger().dev_dependencies()
        assert "django-stubs" in result


class TestProjectTester:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ProjectTester().dev_dependencies()
        assert "pytest-django" in result
