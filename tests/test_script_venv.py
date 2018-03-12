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
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'script_venv.cli.main' in result.output


def test_cli_help(runner):
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
