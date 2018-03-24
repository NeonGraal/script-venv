# -*- coding: utf-8 -*-

""" Config file processing """

from typing import Callable, cast

import pytest

from script_venv.config import VenvConfig
from .factory import TestConfigDependencies

# noinspection SpellCheckingInspection
_SAMPLE_CFG = """[SCRIPTS]
sample.py = sample
pip = sample
pipdeptree = pip.test

[pip.test]
global
prerequisites = wheel
requirements = pipdeptree
"""


class VenvConfigFixtures(object):
    @pytest.fixture
    def deps(self) -> TestConfigDependencies:
        return TestConfigDependencies()

    @pytest.fixture
    def config(self, deps) -> VenvConfig:
        return VenvConfig(deps=deps)


class TestVenvConfig(VenvConfigFixtures):
    @staticmethod
    def test_venv_config_load(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[SCRIPTS]\nsample.py=sample"

        config.load(False)

        assert 'sample.py' in config.scripts
        assert 'sample' in config.venvs
        assert 'sample' == config.scripts['sample.py']

    @staticmethod
    def test_venv_config_scripts(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[SCRIPTS]\nsample.py=sample\npip=sample"

        config.load(False)

        assert {'sample.py', 'pip'} <= set(config.scripts)

    @staticmethod
    def test_venv_config_venvs(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[sample]\n[pip]\n"

        config.load(False)

        assert {'sample', 'pip'} <= set(config.venvs)

    @staticmethod
    def test_venv_config_ignored(config: VenvConfig,
                                 click_iso: Callable) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[Sample]\n[pip.Test]\n"

        with click_iso() as out:
            config.load(False)
            click_out = out.getvalue()

        assert not config.venvs
        assert b"Sample, pip.Test" in click_out


class TestVenvConfigDetails(VenvConfigFixtures):
    @staticmethod
    def test_venv_prerequisites(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[sample]\nprerequisites = first\n\tsecond\n"

        config.load(False)

        venv = config.venvs['sample']
        assert {'first', 'second'} == venv.prerequisites

    @staticmethod
    def test_venv_requirements(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[sample]\nrequirements = alpha\n\tbeta\n"

        config.load(False)

        venv = config.venvs['sample']
        assert {'alpha', 'beta'} == venv.requirements


class TestVenvConfigLocation(VenvConfigFixtures):
    @staticmethod
    def test_venv_current(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[pip.test]\n"

        config.load(False)

        assert '~' not in str(config.venvs['pip.test'])

    @staticmethod
    def test_venv_user(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[pip.test]\n"

        config.load(True)

        assert '~' in str(config.venvs['pip.test'])

    @staticmethod
    def test_venv_global(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[pip.test]\nglobal\n"

        config.load(False)

        assert '~' in str(config.venvs['pip.test'])

    @staticmethod
    def test_venv_local(config: VenvConfig) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = "[pip.test]\nlocal\n"

        config.load(True)

        assert '~' not in str(config.venvs['pip.test'])


class TestVenvConfigRegister(VenvConfigFixtures):
    @staticmethod
    def test_register(config: VenvConfig,
                      click_iso: Callable) -> None:
        with click_iso() as out:
            config.register('test', ('package',), False, True)
            click_out = out.getvalue()

        deps = cast(TestConfigDependencies, config.deps)
        assert b"Registering" in click_out
        assert "[test]" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str

    @staticmethod
    def test_register_local(config: VenvConfig,
                            click_iso: Callable) -> None:
        with click_iso() as out:
            config.register('test', ('package',), True, True)
            click_out = out.getvalue()

        deps = cast(TestConfigDependencies, config.deps)
        assert b"Registering" in click_out
        assert "local\n" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str

    @staticmethod
    def test_register_global(config: VenvConfig,
                             click_iso: Callable) -> None:
        with click_iso() as out:
            config.register('test', ('package',), False, False)
            click_out = out.getvalue()

        deps = cast(TestConfigDependencies, config.deps)
        assert b"Registering" in click_out
        assert "global\n" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "local" not in deps.out_str

    @staticmethod
    def test_register_scripts(config: VenvConfig,
                              click_iso: Callable) -> None:
        with click_iso() as out:
            config.register('test', ('package1', 'package2'), False, False)
            click_out = out.getvalue()

        deps = cast(TestConfigDependencies, config.deps)
        assert b"Registering" in click_out
        assert "package1.script = test" in deps.out_str
        assert "package2.script = test" in deps.out_str
        assert "requirements = package1\n\tpackage2" in deps.out_str

    @staticmethod
    def test_register_user(config: VenvConfig,
                           click_iso: Callable) -> None:
        with click_iso() as out:
            config.register('test', ('package',), True, False)
            click_out = out.getvalue()

        deps = cast(TestConfigDependencies, config.deps)
        assert b"Registering" in click_out
        assert "[test]" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str

    @staticmethod
    def test_register_existing(config: VenvConfig,
                               click_iso: Callable) -> None:
        deps = cast(TestConfigDependencies, config.deps)
        deps.in_str = """[SCRIPTS]
sample = test

[test]
prerequisites = early
requirements = old
"""

        with click_iso() as out:
            config.register('test', ('new',), True, False)
            click_out = out.getvalue()

        deps = cast(TestConfigDependencies, config.deps)
        assert b"Registering" in click_out
        assert "[test]" in deps.out_str
        assert "[SCRIPTS]" in deps.out_str
        assert "prerequisites = early" in deps.out_str
        assert "requirements = new\n\told" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str
