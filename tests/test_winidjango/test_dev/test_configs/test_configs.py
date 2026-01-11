"""module."""

from winidjango.dev.configs.configs import PyprojectConfigFile


class TestPyprojectConfigFile:
    """Test class."""

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        deps = PyprojectConfigFile.get_dev_dependencies()
        assert isinstance(deps, list)
        assert "django-stubs" in deps
        assert "pytest-django" in deps
