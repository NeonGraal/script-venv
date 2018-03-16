#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

import pytest

from click.testing import CliRunner

# from script_venv import script_venv
from script_venv import cli


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_default(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_script(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['script'])
    assert result.exit_code == 0
    assert 'script args' in result.output


def test_cli_script_with_args(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['script', 'arg1', 'arg2'])
    assert result.exit_code == 0
    assert 'script args' in result.output


def test_cli_script_with_opts(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['script', '-o', '--opt'])
    assert result.exit_code == 0
    assert 'script args' in result.output


def test_cli_script_with_args_and_opts(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['script', 'arg1', '-o', 'arg2', '--opts'])
    assert result.exit_code == 0
    assert 'script args' in result.output


def test_cli_version(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['--version'])
    assert result.exit_code == 0
    assert 'sv, version' in result.output


def test_cli_help(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_update(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, [':update', 'venv'])
    assert result.exit_code == 0
    assert 'update venv' in result.output


def test_cli_update_help(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, [':update', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output
