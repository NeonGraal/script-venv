# -*- coding: utf-8 -*-

""" Config file processing """

from os import getcwd, chdir, path
from pathlib import Path
import pytest
from typing import Iterable

from script_venv.config import VenvConfig


@pytest.fixture
def config() -> Iterable[VenvConfig]:
    old_path = getcwd()
    try:
        chdir(path.dirname(__file__))
        config = VenvConfig()
        config.load(Path('.'), True)
        yield config
    finally:
        chdir(old_path)


def test_config_missing() -> None:
    config = VenvConfig()
    config.load(Path(path.expanduser('~')) / 'test', True)
    assert [] == list(config.venvs)


def test_config_load(config: VenvConfig) -> None:
    assert 'sample.py' in config.scripts
    assert 'sample' in config.venvs


def test_config_venv(config: VenvConfig) -> None:
    assert 'sample' == config.scripts['sample.py']


def test_config_scripts(config: VenvConfig) -> None:
    assert {'pip', 'sample.py'} <= set(config.scripts)


def test_config_venvs(config: VenvConfig) -> None:
    assert {'sample'} <= set(config.venvs)


def test_venv_global(config: VenvConfig) -> None:
    assert '~' in str(config.venvs['pip.test'])
