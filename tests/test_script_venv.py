#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

from click.testing import CliRunner
# from script_venv import script_venv

from script_venv import cli
from os import getcwd, chdir
import pytest


@pytest.fixture()
def runner():
    old_cwd = getcwd()
    try:
        chdir('tests')
        yield CliRunner()
    finally:
        chdir(old_cwd)


def test_cli_default(runner: CliRunner) -> None:
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, ['--version'])
    assert result.exit_code == 0
    assert 'sv, version' in result.output


def test_cli_help(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_register_help(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, [':register', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_list(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, [':list'])
    assert result.exit_code == 0
    assert 'Configs:' in result.output


def test_cli_list_help(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, [':list', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_sample(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, ['Sample', '-m', 'pip', 'list'])
    assert result.exit_code == 0


def test_cli_sample_script(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, ['Sample.py'])
    assert result.exit_code == 0


def test_cli_pip(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, ['pip', 'list'])
    assert result.exit_code == 0
