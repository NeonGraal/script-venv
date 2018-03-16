#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

from click.testing import CliRunner
# from script_venv import script_venv

from script_venv import cli
from os import getcwd
import pytest


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_default(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


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


def test_cli_update_help(runner):
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, [':update', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_sample(runner: CliRunner) -> None:
    # type: (CliRunner) -> None
    result = runner.invoke(cli.main, ['Sample.py'])
    assert result.exit_code == 0
    assert getcwd() in result.output
