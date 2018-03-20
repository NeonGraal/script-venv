# -*- coding: utf-8 -*-

""" Config file processing """
from io import StringIO
from os import getcwd, chdir
import pytest
from typing import Iterable

from script_venv.config import VenvConfig

# noinspection SpellCheckingInspection
_SAMPLE_CFG = """[SCRIPTS]
sample.py = sample
pip = sample
pipdeptree = pip.test

[pip.test]
global
requirements = pipdeptree
"""


@pytest.fixture
def restore_cwd() -> Iterable[str]:
    old_path = getcwd()
    try:
        yield old_path
    finally:
        chdir(old_path)


@pytest.fixture
def venv_config() -> VenvConfig:
    return VenvConfig()


def venv_config_load(venv_config: VenvConfig) -> None:
    venv_config.load(False, in_file=StringIO("[SCRIPTS]\nsample.py=sample"))

    assert 'sample.py' in venv_config.scripts
    assert 'sample' in venv_config.venvs
    assert 'sample' == venv_config.scripts['sample.py']


def venv_config_scripts(venv_config: VenvConfig) -> None:
    venv_config.load(False, in_file=StringIO("[SCRIPTS]\nsample.py=sample\npip=sample"))

    assert {'pip', 'sample.py'} <= set(venv_config.scripts)


def venv_config_venvs(venv_config: VenvConfig) -> None:
    venv_config.load(False, in_file=StringIO("[sample]\n[pip]"))

    assert {'sample', 'pip'} <= set(venv_config.venvs)


def test_venv_current(venv_config: VenvConfig) -> None:
    venv_config.load(False, in_file=StringIO("[pip.test]\n"))

    assert '~' not in str(venv_config.venvs['pip.test'])


def test_venv_user(venv_config: VenvConfig) -> None:
    venv_config.load(True, in_file=StringIO("[pip.test]\n"))

    assert '~' in str(venv_config.venvs['pip.test'])


def test_venv_global(venv_config: VenvConfig) -> None:
    venv_config.load(False, in_file=StringIO("[pip.test]\nglobal"))

    assert '~' in str(venv_config.venvs['pip.test'])


def test_venv_local(venv_config: VenvConfig) -> None:
    venv_config.load(True, in_file=StringIO("[pip.test]\nlocal"))

    assert '~' not in str(venv_config.venvs['pip.test'])


def test_register(venv_config: VenvConfig) -> None:
    out_file = StringIO()

    def test_scripts(_package: str) -> Iterable[str]:
        return []

    venv_config.register('test', ('package',), False, True, out_file=out_file, package_scripts=test_scripts)

    out_str = out_file.getvalue()
    assert "[test]" in out_str
    assert "requirements = package" in out_str
    assert "global" not in out_str
    assert "local" not in out_str


def test_register_user(venv_config: VenvConfig) -> None:
    out_file = StringIO()

    def test_scripts(_package: str) -> Iterable[str]:
        return []

    venv_config.register('test', ('package',), True, False, out_file=out_file, package_scripts=test_scripts)

    out_str = out_file.getvalue()
    assert "[test]" in out_str
    assert "requirements = package" in out_str
    assert "global" not in out_str
    assert "local" not in out_str


def test_register_local(venv_config: VenvConfig) -> None:
    out_file = StringIO()

    def test_scripts(_package: str) -> Iterable[str]:
        return []

    venv_config.register('test', ('package',), True, True, out_file=out_file, package_scripts=test_scripts)

    out_str = out_file.getvalue()
    assert "local\n" in out_str
    assert "requirements = package" in out_str
    assert "global" not in out_str


def test_register_global(venv_config: VenvConfig) -> None:
    out_file = StringIO()

    def test_scripts(_package: str) -> Iterable[str]:
        return []

    venv_config.register('test', ('package',), False, False, out_file=out_file, package_scripts=test_scripts)

    out_str = out_file.getvalue()
    assert "global\n" in out_str
    assert "requirements = package" in out_str
    assert "local" not in out_str


def test_register_scripts(venv_config: VenvConfig) -> None:
    out_file = StringIO()

    def test_scripts(package: str) -> Iterable[str]:
        return [package + '.script']

    venv_config.register('test', ('package1', 'package2'), False, False,
                         out_file=out_file, package_scripts=test_scripts)

    out_str = out_file.getvalue()
    assert "package1.script = test" in out_str
    assert "package2.script = test" in out_str
    assert "requirements = package1\n\tpackage2" in out_str
