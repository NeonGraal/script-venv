#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

from os import getcwd, chdir, path
from typing import Iterable, cast, Any
from unittest.mock import Mock, ANY

import pytest
from click.testing import CliRunner, Result

from script_venv import cli
from script_venv.config import ConfigDependencies, VenvConfig
from script_venv.venv import VEnvDependencies
from tests.test_config import VenvConfigFixtures
from tests.utils import config_write, config_scripts, config_read


class CliDependenciesRunner(CliRunner):
    def __init__(self, deps: ConfigDependencies, **kwargs) -> None:
        self.deps = deps
        super(CliDependenciesRunner, self).__init__(**kwargs)

    def invoke(self, cli: Any, *args: Any, **kwargs: Any) -> Result:
        kwargs['deps'] = self.deps
        return super(CliDependenciesRunner, self).invoke(cli, *args, **kwargs)


class CliObjectRunner(CliRunner):
    def __init__(self, obj: Any, **kwargs) -> None:
        self.obj = obj
        super(CliObjectRunner, self).__init__(**kwargs)

    def invoke(self, cli, *args, **extra):
        extra['obj'] = self.obj
        return super(CliObjectRunner, self).invoke(cli, *args, **extra)


class CliFixtures(VenvConfigFixtures):
    @pytest.fixture
    def run_deps(self, config_deps: ConfigDependencies) -> Iterable[CliRunner]:
        old_cwd = getcwd()
        try:
            chdir(path.dirname(__file__))
            yield CliObjectRunner(config_deps)
        finally:
            chdir(old_cwd)

    @pytest.fixture
    def mock_config(self) -> Mock:
        return Mock(spec=VenvConfig)

    @pytest.fixture
    def run_config(self, mock_config: Mock) -> CliRunner:
        old_cwd = getcwd()
        try:
            chdir(path.dirname(__file__))
            yield CliObjectRunner(mock_config)
        finally:
            chdir(old_cwd)


class TestCli(CliFixtures):
    def test_cli_default(self, run_config: CliRunner):
        result = run_config.invoke(cli.main)

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_version(self, run_config: CliRunner):
        result = run_config.invoke(cli.main, ['--version'])

        assert result.exit_code == 0
        assert 'sv, version' in result.output

    def test_cli_help(self, run_config: CliRunner):
        result = run_config.invoke(cli.main, ['--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_register_help(self, run_config: CliRunner):
        result = run_config.invoke(cli.main, [':register', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_create_help(self, run_config: CliRunner):
        result = run_config.invoke(cli.main, [':create', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_list_help(self, run_config: CliRunner) -> None:
        result = run_config.invoke(cli.main, [':list', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output


class TestCliOptions(CliFixtures):
    def test_cli_search_path(self,
                             mock_config: Mock,
                             run_config: CliRunner):
        run_config.invoke(cli.main, ['-S', 'Test', 'test'])

        mock_config.search_path.assert_called_with('Test')


class TestCliDeep(CliFixtures):
    def test_cli_register_sample(self,
                                 config_deps: ConfigDependencies,
                                 run_deps: CliRunner) -> None:
        deps = cast(Mock, config_deps)
        config_read(deps, {
            self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = sample\npipdeptree = pip.test\n\n"
                             "[pip.test]\nrequirements = pipdeptree\n"
        })
        config_write(deps)
        config_scripts(deps)

        result = run_deps.invoke(cli.main, [':register', 'sample', 'pipdeptree'])

        assert result.exit_code == 0
        assert 'Registering pipdeptree.script from pipdeptree into sample' in result.output

    def test_cli_create_update(self,
                               config_deps: ConfigDependencies,
                               run_deps: CliRunner) -> None:
        deps = cast(Mock, config_deps)
        config_read(deps, {
            self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = sample\npipdeptree = pip.test\n\n"
                             "[pip.test]\nrequirements = pipdeptree\n"
        })

        result = run_deps.invoke(cli.main, [':create', 'sample', '--update'])

        assert result.exit_code == 0
        assert 'Creating venv sample' in result.output

    def test_cli_list(self, run_deps: CliRunner) -> None:
        result = run_deps.invoke(cli.main, [':list'])

        assert result.exit_code == 0
        assert 'Configs:' in result.output

    def test_cli_sample(self,
                        venv_deps: VEnvDependencies,
                        config_deps: ConfigDependencies,
                        run_deps: CliRunner) -> None:
        config_read(cast(Mock, config_deps), {
            self.CWD_sv_cfg: "[SCRIPTS]\nSample.py = sample\npipdeptree = pip.test\n\n"
                             "[pip.test]\nrequirements = pipdeptree\n"
        })

        result = run_deps.invoke(cli.main, ['sample', '--version'])

        assert result.exit_code == 1
        deps = cast(Mock, venv_deps)
        deps.runner.assert_called_with([ANY, '--version'], env=ANY)
