# -*- coding: utf-8 -*-

""" Config file processing """
from os import getcwd, chdir
import pytest
from typing import Iterable

from script_venv.config import VenvConfig

from .factory import TestConfigDependencies

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


class TestVenvConfig(object):
    @pytest.fixture
    def deps(self) -> TestConfigDependencies:
        return TestConfigDependencies()

    @pytest.fixture
    def config(self, deps) -> VenvConfig:
        return VenvConfig(deps=deps)

    @staticmethod
    def venv_config_load(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[SCRIPTS]\nsample.py=sample"

        config.load(False)

        assert 'sample.py' in config.scripts
        assert 'sample' in config.venvs
        assert 'sample' == config.scripts['sample.py']

    @staticmethod
    def venv_config_scripts(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[SCRIPTS]\nsample.py=sample\npip=sample"

        config.load(False)

        assert {'pip', 'sample.py'} <= set(config.scripts)

    @staticmethod
    def venv_config_venvs(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[sample]\n[pip]\n"

        config.load(False)

        assert {'sample', 'pip'} <= set(config.venvs)

    @staticmethod
    def test_venv_current(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[pip.test]\n"

        config.load(False)

        assert '~' not in str(config.venvs['pip.test'])

    @staticmethod
    def test_venv_user(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[pip.test]\n"

        config.load(True)

        assert '~' in str(config.venvs['pip.test'])

    @staticmethod
    def test_venv_global(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[pip.test]\nglobal\n"

        config.load(False)

        assert '~' in str(config.venvs['pip.test'])

    @staticmethod
    def test_venv_local(config: VenvConfig, deps: TestConfigDependencies) -> None:
        deps.in_str = "[pip.test]\nlocal\n"

        config.load(True)

        assert '~' not in str(config.venvs['pip.test'])

    @staticmethod
    def test_register(config: VenvConfig, deps: TestConfigDependencies) -> None:
        config.register('test', ('package',), False, True)

        assert "[test]" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str

    @staticmethod
    def test_register_user(config: VenvConfig, deps: TestConfigDependencies) -> None:
        config.register('test', ('package',), True, False)

        assert "[test]" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str

    @staticmethod
    def test_register_local(config: VenvConfig, deps: TestConfigDependencies) -> None:
        config.register('test', ('package',), True, True)

        assert "local\n" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str

    @staticmethod
    def test_register_global(config: VenvConfig, deps: TestConfigDependencies) -> None:
        config.register('test', ('package',), False, False)

        assert "global\n" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "local" not in deps.out_str

    @staticmethod
    def test_register_scripts(config: VenvConfig, deps: TestConfigDependencies) -> None:
        def test_scripts(package: str) -> Iterable[str]:
            return [package + '.script']

        config.register('test', ('package1', 'package2'), False, False)

        assert "package1.script = test" in deps.out_str
        assert "package2.script = test" in deps.out_str
        assert "requirements = package1\n\tpackage2" in deps.out_str
