#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

from os import getcwd, chdir, path
from typing import Iterable
from unittest.mock import Mock

import pytest

from script_venv import cli
from script_venv.config import VenvConfig

from .utils import CliObjectRunner


class CliFixtures(object):
    @pytest.fixture
    def mock_config(self) -> Mock:
        return Mock(spec=VenvConfig)

    @pytest.fixture
    def run_config(self, mock_config: Mock) -> Iterable[CliObjectRunner]:
        old_cwd = getcwd()
        try:
            chdir(path.dirname(__file__))
            yield CliObjectRunner(mock_config)
        finally:
            chdir(old_cwd)


class TestCliHelp(CliFixtures):
    def test_cli_default(self, run_config: CliObjectRunner):
        result = run_config.invoke(cli.main)

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_version(self, run_config: CliObjectRunner):
        result = run_config.invoke(cli.main, ['--version'])

        assert result.exit_code == 0
        assert 'sv, version' in result.output

    def test_cli_help(self, run_config: CliObjectRunner):
        result = run_config.invoke(cli.main, ['--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_register_help(self, run_config: CliObjectRunner):
        result = run_config.invoke(cli.main, [':register', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_create_help(self, run_config: CliObjectRunner):
        result = run_config.invoke(cli.main, [':create', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_list_help(self, run_config: CliObjectRunner) -> None:
        result = run_config.invoke(cli.main, [':list', '--help'])

        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output


class TestCliOptions(CliFixtures):
    def test_cli_search_path(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, ['-S', 'Test', 'test'])

        mock_config.search_path.assert_called_once_with('Test')
        mock_config.load.assert_called_once_with()

    def test_cli_list(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':list'])

        mock_config.load.assert_called_once_with()
        mock_config.list.assert_called_once_with()

    def test_cli_create(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_not_called()

    def test_cli_create_venv(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=False, update=False)

    def test_cli_create_params(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test', 'param1', 'param2'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', 'param1', 'param2', clean=False, update=False)

    def test_cli_create_clean(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test', '-C'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=True, update=False)

    def test_cli_create_update(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test', '-U'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=False, update=True)

    def test_cli_register(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_not_called()

    def test_cli_register_venv(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_not_called()

    def test_cli_register_package(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package', ), config_path=None, venv_path=None)

    def test_cli_register_packages(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package1', 'package2'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package1', 'package2'), config_path=None, venv_path=None)

    def test_cli_register_config_path(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package', '-P', 'config_path'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package', ), config_path='config_path', venv_path=None)

    def test_cli_register_venv_path(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package', '-V', 'venv_path'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package', ), config_path=None, venv_path='venv_path')
