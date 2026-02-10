"""module."""

from winidjango.rig.tools.tools import ProjectTester, Pyrigger


class TestPyrigger:
    """Test class."""

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = Pyrigger.get_dev_dependencies()
        assert "django-stubs" in result


class TestProjectTester:
    """Test class."""

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = ProjectTester.get_dev_dependencies()
        assert "pytest-django" in result
