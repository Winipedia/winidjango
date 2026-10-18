"""Tests for Django initialization from installed entry points."""

import subprocess
import sys
from pathlib import Path


def test_initialization_without_repository_on_sys_path() -> None:
    """Configure the local tests app even when Python excludes the working directory."""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "from pathlib import Path; "
                "import winidjango; "
                "from django.apps import apps; "
                "assert apps.ready; "
                "assert Path(apps.get_app_config('tests').path).resolve() "
                "== Path('tests').resolve()"
            ),
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
