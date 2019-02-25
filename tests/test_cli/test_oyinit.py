import os
import pytest
from click.testing import CliRunner
from oy.cli.oyinit import init_oy_project


runner = CliRunner()


def test_oyinit_basic(app):
    project_name = "test_project"
    with runner.isolated_filesystem():
        result = runner.invoke(init_oy_project, [project_name])
        assert os.path.exists(f"./{project_name}")
        assert os.path.exists(f"./{project_name}/{project_name}/config.py")
        assert os.path.exists(f"./{project_name}/.flaskenv")
    assert result.exit_code == 0
    assert project_name in result.output
