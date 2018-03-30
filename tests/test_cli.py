#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package."""

from os import getcwd, chdir, path
from typing import Iterable, cast

import pytest
from click.testing import CliRunner

from script_venv import cli
from tests.factory import TestConfigDependencies, TestVEnvDependencies


class CliDependenciesRunner(CliRunner):
    def __init__(self, **kwargs):
        self.deps = TestConfigDependencies()
        self.deps.in_str = """[SCRIPTS]
Sample.py = sample
pipdeptree = pip.test

[pip.test]
requirements = pipdeptree
"""
        super(CliDependenciesRunner, self).__init__(**kwargs)

    def invoke(self, cli: object, args: Iterable[str] = None, **kwargs: object):
        return super(CliDependenciesRunner, self).invoke(cli, args=args, deps=self.deps, **kwargs)


@pytest.fixture
def runner() -> Iterable[CliDependenciesRunner]:
    old_cwd = getcwd()
    try:
        chdir(path.dirname(__file__))
        yield CliDependenciesRunner()
    finally:
        chdir(old_cwd)


def test_cli_default(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_version(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, ['--version'])
    assert result.exit_code == 0
    assert 'sv, version' in result.output


def test_cli_help(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_register_help(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, [':register', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_register_sample(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, [':register', 'sample', 'pipdeptree'])
    assert result.exit_code == 0
    assert 'Registering pipdeptree.script from pipdeptree into sample' in result.output


def test_cli_create_help(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, [':create', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_create_update(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, [':create', 'sample', '--update'])
    assert result.exit_code == 0
    assert 'Creating venv sample' in result.output


def test_cli_list(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, [':list'])
    assert result.exit_code == 0
    assert 'Configs:' in result.output


def test_cli_list_help(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, [':list', '--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output


def test_cli_sample(runner: CliDependenciesRunner) -> None:
    result = runner.invoke(cli.main, ['sample', '--version'])
    venv_deps = cast(TestVEnvDependencies, runner.deps.venv_deps())
    assert result.exit_code == -1
    assert '--version' in venv_deps.run_args[0]
