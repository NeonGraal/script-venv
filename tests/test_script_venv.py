# -*- coding: utf-8 -*-

""" Test script_venv routines """
from unittest.mock import Mock, ANY

from script_venv import cli

from .test_config import VenvConfigFixtures
from .utils import config_read, venv_exists, CliObjectRunner, StringContaining


class TestCliScripts(VenvConfigFixtures):
    def test_cli_script_exists(self, venv_deps: Mock, config_deps: Mock):
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = test\n\n[test]"})
        venv_exists(venv_deps, self.CWD_sv_test)

        CliObjectRunner(config_deps).invoke(cli.main, ['Sample.py', '--version'])

        assert not venv_deps.creator.called
        venv_deps.runner.assert_called_once_with([ANY, 'Sample.py', '--version'], env=ANY)

    def test_cli_script_missing(self, venv_deps: Mock, config_deps: Mock):
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = test\n\n[test]"})
        venv_exists(venv_deps)

        CliObjectRunner(config_deps).invoke(cli.main, ['Sample.py', '--version'])

        assert venv_deps.creator.called
        venv_deps.runner.assert_any_call([ANY, 'Sample.py', '--version'], env=ANY)

    def test_cli_venv_exists(self, venv_deps: Mock, config_deps: Mock):
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = test\n\n[test]"})
        venv_exists(venv_deps, self.CWD_sv_test)

        CliObjectRunner(config_deps).invoke(cli.main, ['test', '--version'])

        assert not venv_deps.creator.called
        venv_deps.runner.assert_called_once_with([StringContaining('test'), '--version'], env=ANY)

    def test_cli_venv_missing(self, venv_deps: Mock, config_deps: Mock):
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = test\n\n[test]"})
        venv_exists(venv_deps)

        CliObjectRunner(config_deps).invoke(cli.main, ['test', '--version'])

        assert venv_deps.creator.called
        venv_deps.runner.assert_any_call([StringContaining('test'), '--version'], env=ANY)
