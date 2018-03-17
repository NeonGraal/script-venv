# -*- coding: utf-8 -*-

""" Config file processing """
from pathlib import Path

import pytest
from os import getcwd, chdir, path

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


def test_config_missing():
    config = VenvConfig()
    config.load(Path.home() / 'test', True)
    assert [] == list(config.venvs)


def test_config_load(config: VenvConfig):
    assert 'sample.py' in config.scripts
    assert 'sample' in config.venvs


def test_config_venv(config: VenvConfig):
    assert 'sample' == config.scripts['sample.py']


def test_config_scripts(config: VenvConfig):
    assert ['pip', 'sample.py'] == sorted(config.scripts)


def test_config_venvs(config: VenvConfig):
    assert ['sample'] == sorted(config.venvs)
