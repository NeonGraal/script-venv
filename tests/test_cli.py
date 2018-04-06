#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

from os import getcwd, chdir, path
from typing import Iterable, cast
from unittest.mock import Mock, ANY

import pytest
from click.testing import CliRunner, Result

from script_venv import cli
from script_venv.config import ConfigDependencies
from script_venv.venv import VEnvDependencies
from tests.test_config import VenvConfigFixtures
from tests.utils import config_write, config_scripts, config_read


class CliDependenciesRunner(CliRunner):
    def __init__(self, deps: ConfigDependencies, **kwargs) -> None:
        self.deps = deps
        super(CliDependenciesRunner, self).__init__(**kwargs)

    def invoke(self, cli: object, args: Iterable[str] = None, **kwargs: object) -> Result:
        return super(CliDependenciesRunner, self).invoke(cli, args=args, deps=self.deps, **kwargs)


class CliFixtures(VenvConfigFixtures):
    @pytest.fixture
    def runner(self, config_deps: ConfigDependencies) -> Iterable[CliDependenciesRunner]:
        old_cwd = getcwd()
        try:
            chdir(path.dirname(__file__))
            yield CliDependenciesRunner(config_deps)
        finally:
            chdir(old_cwd)


class TestCli(CliFixtures):
    def test_cli_default(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main)

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_version(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main, ['--version'])

        assert result.exit_code == 0
        assert 'sv, version' in result.output

    def test_cli_help(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main, ['--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_register_help(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main, [':register', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_register_sample(self,
                                 config_deps: ConfigDependencies,
                                 runner: CliDependenciesRunner) -> None:
        deps = cast(Mock, config_deps)
        config_read(deps, {
            self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = sample\npipdeptree = pip.test\n\n"
                             "[pip.test]\nrequirements = pipdeptree\n"
        })
        config_write(deps)
        config_scripts(deps)

        result = runner.invoke(cli.main, [':register', 'sample', 'pipdeptree'])

        assert result.exit_code == 0
        assert 'Registering pipdeptree.script from pipdeptree into sample' in result.output

    def test_cli_create_help(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main, [':create', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_create_update(self,
                               config_deps: ConfigDependencies,
                               runner: CliDependenciesRunner) -> None:
        deps = cast(Mock, config_deps)
        config_read(deps, {
            self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = sample\npipdeptree = pip.test\n\n"
                             "[pip.test]\nrequirements = pipdeptree\n"
        })

        result = runner.invoke(cli.main, [':create', 'sample', '--update'])

        assert result.exit_code == 0
        assert 'Creating venv sample' in result.output

    def test_cli_list(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main, [':list'])

        assert result.exit_code == 0
        assert 'Configs:' in result.output

    def test_cli_list_help(self, runner: CliDependenciesRunner) -> None:
        result = runner.invoke(cli.main, [':list', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_sample(self,
                        venv_deps: VEnvDependencies,
                        config_deps: ConfigDependencies,
                        runner: CliDependenciesRunner) -> None:
        config_read(cast(Mock, config_deps), {
            self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = sample\npipdeptree = pip.test\n\n"
                             "[pip.test]\nrequirements = pipdeptree\n"
        })

        result = runner.invoke(cli.main, ['sample', '--version'])

        assert result.exit_code == 1
        deps = cast(Mock, venv_deps)
        deps.runner.assert_called_with([ANY, '--version'], env=ANY)
