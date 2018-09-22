#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package cli help."""


from script_venv import cli
from tests.cli.fixtures import CliFixtures
from tests.utils import CliObjectRunner


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
