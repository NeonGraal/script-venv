# -*- coding: utf-8 -*-

""" Config file processing """
from os import path
from typing import Callable, cast
from unittest.mock import Mock, MagicMock

import pytest

from script_venv.config import VenvConfig, ConfigDependencies
from script_venv.venv import VEnvDependencies
from tests.test_venv import VEnvFixtures
from tests.utils import config_read, config_write, venv_exists, config_scripts


class VenvConfigFixtures(VEnvFixtures):
    USER_sv_cfg = path.expanduser(path.join('~', '.config', '.sv_cfg'))
    TEST_sv_cfg = path.abspath(path.join('TEST', '.sv_cfg'))
    CWD_sv_cfg = path.expandvars(path.join('$CWD', '.sv_cfg'))

    @pytest.fixture
    def config_deps(self, venv_deps: VEnvDependencies) -> Mock:
        config_mock = MagicMock(spec=ConfigDependencies, name="config_deps")
        config_mock.venv_deps.return_value = venv_deps
        return config_mock

    @pytest.fixture
    def config(self, config_deps: ConfigDependencies) -> VenvConfig:
        return VenvConfig(deps=config_deps)


class TestVenvConfig(VenvConfigFixtures):
    def test_venv_config_load(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[SCRIPTS]\nsample.py=sample"})

        config.load()

        assert 'sample.py' in config.scripts
        assert 'sample' in config.venvs
        assert 'sample' == config.scripts['sample.py']

    def test_venv_config_scripts(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[SCRIPTS]\nsample.py=sample\npip=sample"})

        config.load()

        assert {'sample.py', 'pip'} <= set(config.scripts)

    def test_venv_config_venvs(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[sample]\n[pip]\n"})

        config.load()

        assert {'sample', 'pip'} <= set(config.venvs)

    def test_venv_config_ignored(self,
                                 config_deps: Mock,
                                 config: VenvConfig,
                                 click_iso: Callable) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[Sample]\n[pip.Test]\n"})

        with click_iso() as out:
            config.load()
            click_out = out.getvalue()

        assert not config.venvs
        assert b"Sample, pip.Test" in click_out


class TestVenvConfigDetails(VenvConfigFixtures):
    def test_venv_prerequisites(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[sample]\nprerequisites = first\n\tsecond\n"})

        config.load()

        venv = config.venvs['sample']
        assert {'first', 'second'} == venv.prerequisites

    def test_venv_requirements(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[sample]\nrequirements = alpha\n\tbeta\n"})

        config.load()

        venv = config.venvs['sample']
        assert {'alpha', 'beta'} == venv.requirements


class TestVenvConfigLocation(VenvConfigFixtures):
    def test_venv_current(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[pip.test]\n"})

        config.load()

        assert '~' not in str(config.venvs['pip.test'])

    def test_venv_user(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.USER_sv_cfg: "[pip.test]\n"})

        config.load()

        assert '~' in str(config.venvs['pip.test'])

    def test_venv_local(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[pip.test]\nlocation = ~\n"})

        config.load()

        assert '~' in str(config.venvs['pip.test'])


class TestVenvConfigList(VenvConfigFixtures):
    def test_list_empty(self,
                        config: VenvConfig,
                        click_iso: Callable) -> None:
        with click_iso() as out:
            config.list()
            click_out = out.getvalue()

        assert b"Configs: []" == click_out.strip()

    def test_list_basic(self,
                        config_deps: Mock,
                        config: VenvConfig,
                        click_iso: Callable) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[test]\n"})

        config.load()
        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert path.join("[TEST", ".sv_cfg]") in click_out
        assert path.join('test (TEST', '.sv', 'test)') in click_out

    def test_list_requirements(self,
                               config_deps: Mock,
                               config: VenvConfig,
                               click_iso: Callable) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[test]\nrequirements = second\n\tfirst\n"})
        config.load()

        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert "\tRequirements: first" in click_out
        assert "\t\tsecond" in click_out

    def test_list_prerequisites(self,
                                config_deps: Mock,
                                config: VenvConfig,
                                click_iso: Callable) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[test]\nprerequisites = beta\n\talpha\n"})
        config.load()

        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert "\tPrerequisites: alpha" in click_out
        assert "\t\tbeta" in click_out

    def test_list_scripts(self,
                          config_deps: Mock,
                          config: VenvConfig,
                          click_iso: Callable) -> None:
        config_read(config_deps, {self.TEST_sv_cfg: "[SCRIPTS]\nsample = test\ntester = test"})
        config.load()

        with click_iso() as out:
            config.list()
            click_out = out.getvalue().decode()

        assert "\tScripts: sample, tester" in click_out


class TestVenvConfigRegister(VenvConfigFixtures):
    def test_register(self,
                      config_deps: Mock,
                      config: VenvConfig,
                      click_iso: Callable) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='testing')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        testing_sv_cfg = path.abspath(path.join('testing', '.sv_cfg'))
        assert testing_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[testing_sv_cfg]
        assert "[test]" in out_str
        assert "requirements = package" in out_str
        assert "global" not in out_str
        assert "local" not in out_str

    def test_register_local(self,
                            config_deps: Mock,
                            config: VenvConfig,
                            click_iso: Callable) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='$CWD')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert self.CWD_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.CWD_sv_cfg]
        assert "requirements = package" in out_str

    def test_register_global(self,
                             config_deps: Mock,
                             config: VenvConfig,
                             click_iso: Callable) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='~/.config')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert self.USER_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.USER_sv_cfg]
        assert "requirements = package" in out_str

    def test_register_scripts(self,
                              config_deps: Mock,
                              config: VenvConfig,
                              click_iso: Callable) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        with click_iso() as out:
            config.register('test', ('package1', 'package2'), config_path='TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert self.TEST_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.TEST_sv_cfg]
        assert "package1.script = test" in out_str
        assert "package2.script = test" in out_str
        assert "requirements = package1\n\tpackage2" in out_str

    def test_register_user(self,
                           config_deps: Mock,
                           config: VenvConfig,
                           click_iso: Callable) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        with click_iso() as out:
            config.register('test', ('package',), config_path='$CWD')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert self.CWD_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.CWD_sv_cfg]
        assert "[test]" in out_str
        assert "requirements = package" in out_str
        assert "global" not in out_str
        assert "local" not in out_str

    def test_register_existing(self,
                               config_deps: Mock,
                               config: VenvConfig,
                               click_iso: Callable) -> None:
        config_read(config_deps, {
            self.TEST_sv_cfg: """[SCRIPTS]\nsample = test\n\n[test]\nprerequisites = early\nrequirements = old\n"""
        })
        config_write(config_deps)
        config_scripts(config_deps)

        with click_iso() as out:
            config.register('test', ('new',), config_path='TEST')
            click_out = out.getvalue()

        assert b"Registering" in click_out
        assert self.TEST_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.TEST_sv_cfg]
        assert "[test]" in out_str
        assert "[SCRIPTS]" in out_str
        assert "prerequisites = early" in out_str
        assert "requirements = new\n\told" in out_str
        assert "global" not in out_str
        assert "local" not in out_str


class TestVenvConfigCreate(VenvConfigFixtures):
    def test_create_venv(self,
                         venv_deps: Mock,
                         config_deps: Mock,
                         config: VenvConfig,
                         click_iso: Callable) -> None:
        venv_exists(venv_deps)
        config_read(config_deps, {self.TEST_sv_cfg: "[test]"})
        config.load()

        with click_iso() as out:
            config.create('test')
            click_out = out.getvalue().decode()

        assert "Creating venv test" in click_out

    def test_create_script(self,
                           venv_deps: Mock,
                           config: VenvConfig,
                           click_iso: Callable) -> None:
        venv_exists(cast(Mock, venv_deps))
        config_deps = cast(Mock, config.deps)
        config_read(config_deps, {self.TEST_sv_cfg: "[SCRIPTS]\ntester = test"})
        config.load()

        with click_iso() as out:
            config.create('tester')
            click_out = out.getvalue().decode()

        assert "Creating venv test" in click_out

    def test_create_missing(self,
                            config: VenvConfig,
                            click_iso: Callable) -> None:
        config_deps = cast(Mock, config.deps)
        config_read(config_deps, {self.TEST_sv_cfg: "[test]"})
        config.load()

        with click_iso() as out:
            config.create('other')
            click_out = out.getvalue().decode()

        assert "Unable to find venv or script other" in click_out

    def test_create_exists(self,
                           config: VenvConfig,
                           click_iso: Callable) -> None:
        config_deps = cast(Mock, config.deps)
        venv_deps = cast(Mock, config.deps.venv_deps())
        config_read(config_deps, {self.TEST_sv_cfg: "[test]"})
        venv_exists(venv_deps, self.TEST_sv_test)
        config.load()

        with click_iso() as out:
            config.create('test')
            click_out = out.getvalue().decode()

        assert "" == click_out

    def test_create_clean(self,
                          config: VenvConfig,
                          click_iso: Callable) -> None:
        config_deps = cast(Mock, config.deps)
        venv_deps = cast(Mock, config.deps.venv_deps())
        config_read(config_deps, {self.TEST_sv_cfg: "[test]"})
        venv_exists(venv_deps, self.TEST_sv_test)
        config.load()

        with click_iso() as out:
            config.create('test', clean=True)
            click_out = out.getvalue().decode()

        assert "Cleaning venv test" in click_out

    def test_create_update(self,
                           config: VenvConfig,
                           click_iso: Callable) -> None:
        config_deps = cast(Mock, config.deps)
        venv_deps = cast(Mock, config.deps.venv_deps())
        config_read(config_deps, {self.TEST_sv_cfg: "[test]"})
        venv_exists(venv_deps, self.TEST_sv_test)
        config.load()

        with click_iso() as out:
            config.create('test', update=True)
            click_out = out.getvalue().decode()

        assert "Updating venv test" in click_out
