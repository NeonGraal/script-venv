# -*- coding: utf-8 -*-

""" Config file processing """
import os
from typing import Callable, cast
from unittest.mock import Mock, MagicMock

import pytest

from script_venv.config import VenvConfig, ConfigDependencies
# noinspection SpellCheckingInspection
from tests.utils import config_read, config_write

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
    def deps(self) -> ConfigDependencies:
        return cast(ConfigDependencies, MagicMock(spec=ConfigDependencies))

    @pytest.fixture
    def config(self, deps) -> VenvConfig:
        return VenvConfig(search_path=["$TEST"], deps=deps)


class TestVenvConfig(VenvConfigFixtures):
    def test_venv_config_load(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[SCRIPTS]\nsample.py=sample")

        config.load()

        assert 'sample.py' in config.scripts
        assert 'sample' in config.venvs
        assert 'sample' == config.scripts['sample.py']

    def test_venv_config_scripts(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[SCRIPTS]\nsample.py=sample\npip=sample")

        config.load()

        assert {'sample.py', 'pip'} <= set(config.scripts)

    def test_venv_config_venvs(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[sample]\n[pip]\n")

        config.load()

        assert {'sample', 'pip'} <= set(config.venvs)

    def test_venv_config_ignored(self,
                                 config: VenvConfig,
                                 click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[Sample]\n[pip.Test]\n")

        with click_iso() as out:
            config.load()
            click_out = out.getvalue()

        assert not config.venvs
        assert b"Sample, pip.Test" in click_out


class TestVenvConfigDetails(VenvConfigFixtures):
    def test_venv_prerequisites(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[sample]\nprerequisites = first\n\tsecond\n")

        config.load()

        venv = config.venvs['sample']
        assert {'first', 'second'} == venv.prerequisites

    def test_venv_requirements(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[sample]\nrequirements = alpha\n\tbeta\n")

        config.load()

        venv = config.venvs['sample']
        assert {'alpha', 'beta'} == venv.requirements


class TestVenvConfigLocation(VenvConfigFixtures):
    def test_venv_current(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[pip.test]\n")

        config.load()

        assert '~' not in str(config.venvs['pip.test'])

    def test_venv_user(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[pip.test]\n")

        config.load()

        assert '~' in str(config.venvs['pip.test'])

    def test_venv_global(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[pip.test]\nglobal\n")

        config.load()

        assert '~' in str(config.venvs['pip.test'])

    def test_venv_local(self, config: VenvConfig) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[pip.test]\nlocal\n")

        config.load()

        assert '~' not in str(config.venvs['pip.test'])


class TestVenvConfigList(VenvConfigFixtures):
    def test_list_empty(self,
                        config: VenvConfig,
                        click_iso: Callable) -> None:
        with click_iso() as out:
            config.list()
            click_out = out.getvalue()

        assert b"Configs: []" == click_out.strip()

    def test_list_basic(self,
                        config: VenvConfig,
                        click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]\n")

        config.load()
        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert os.sep.join(["['$TEST", ".sv_cfg']"]) in click_out
        assert os.sep.join(['test (.sv', 'test !MISSING)']) in click_out.splitlines()

    def test_list_requirements(self,
                               config: VenvConfig,
                               click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]\nrequirements = second\n\tfirst\n")

        config.load()
        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert "\tRequirements: first" in click_out
        assert "\t\tsecond" in click_out

    def test_list_prerequisites(self,
                                config: VenvConfig,
                                click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]\nprerequisites = beta\n\talpha\n")

        config.load()
        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert "\tPrerequisites: alpha" in click_out
        assert "\t\tbeta" in click_out

    def test_list_scripts(self,
                          config: VenvConfig,
                          click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[SCRIPTS]\nsample = test\ntester = test")

        config.load()
        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert "\tScripts: sample, tester" in click_out


class TestVenvConfigRegister(VenvConfigFixtures):
    def test_register(self,
                      config: VenvConfig,
                      click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_write(deps)
        deps.scripts.return_value = [('package', 'package.script')]

        with click_iso() as out:
            config.register('test', ('package',), config_path='$TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert "[test]" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str

    def test_register_local(self,
                            config: VenvConfig,
                            click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_write(deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='$TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert "requirements = package" in deps.out_str

    def test_register_global(self,
                             config: VenvConfig,
                             click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_write(deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='$TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert "requirements = package" in deps.out_str

    def test_register_scripts(self,
                              config: VenvConfig,
                              click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_write(deps)

        with click_iso() as out:
            config.register('test', ('package1', 'package2'), config_path='$TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert "package1.script = test" in deps.out_str
        assert "package2.script = test" in deps.out_str
        assert "requirements = package1\n\tpackage2" in deps.out_str

    def test_register_user(self,
                           config: VenvConfig,
                           click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_write(deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='$TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert "[test]" in deps.out_str
        assert "requirements = package" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str

    def test_register_existing(self,
                               config: VenvConfig,
                               click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_write(deps)
        config_read(deps, """[SCRIPTS]\nsample = test\n\n[test]\nprerequisites = early\nrequirements = old\n""")

        with click_iso() as out:
            config.register('test', ('new',), config_path='$TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert "[test]" in deps.out_str
        assert "[SCRIPTS]" in deps.out_str
        assert "prerequisites = early" in deps.out_str
        assert "requirements = new\n\told" in deps.out_str
        assert "global" not in deps.out_str
        assert "local" not in deps.out_str


class TestVenvConfigCreate(VenvConfigFixtures):
    def test_register_create_venv(self,
                                  config: VenvConfig,
                                  click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]")

        config.load()
        with click_iso() as out:
            config.create('test')
            click_out = out.getvalue().decode()

        assert "Creating venv test" in click_out

    def test_register_create_script(self,
                                    config: VenvConfig,
                                    click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[SCRIPTS]\ntester = test")

        config.load()
        with click_iso() as out:
            config.create('tester')
            click_out = out.getvalue().decode()

        assert "Creating venv test" in click_out

    def test_register_create_missing(self,
                                     config: VenvConfig,
                                     click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]")

        config.load()
        with click_iso() as out:
            config.create('other')
            click_out = out.getvalue().decode()

        assert "Unable to find venv or script other" in click_out

    def test_register_create_exists(self,
                                    config: VenvConfig,
                                    click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]")

        config.load()
        deps.test_venv.path_exists = True
        with click_iso() as out:
            config.create('test')
            click_out = out.getvalue().decode()

        assert "" == click_out

    def test_register_create_clean(self,
                                   config: VenvConfig,
                                   click_iso: Callable) -> None:
        deps = cast(Mock, config.deps)
        config_read(deps, "[test]")

        config.load()
        deps.test_venv.path_exists = True
        with click_iso() as out:
            config.create('test', clean=True)
            click_out = out.getvalue().decode()

        assert "Cleaning venv test" in click_out
