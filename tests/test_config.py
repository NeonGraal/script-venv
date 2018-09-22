# -*- coding: utf-8 -*-

""" Test Config file processing """

from os import path
from pathlib2 import Path
from unittest.mock import Mock, MagicMock

import pytest

from script_venv.config import VenvConfig, ConfigDependencies

from .test_venv import VEnvFixtures
from .utils import config_read, config_write, venv_exists, config_scripts, StringContaining


class VenvConfigFixtures(VEnvFixtures):
    USER_sv_cfg = path.expanduser(path.join('~', '.config', '.sv_cfg'))
    CWD_sv_cfg = path.expandvars(path.join('$CWD', '.sv_cfg'))

    @pytest.fixture
    def config_deps(self, venv_deps: Mock) -> Mock:
        config_mock = MagicMock(spec=ConfigDependencies, name="config_deps")
        config_mock.venv_deps.return_value = venv_deps
        return config_mock

    @pytest.fixture
    def config(self, config_deps: ConfigDependencies) -> VenvConfig:
        return VenvConfig(deps=config_deps)


class TestVenvConfig(VenvConfigFixtures):
    def test_venv_config_load(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nsample.py=sample"})

        config.load()

        assert 'sample.py' in config.scripts
        assert 'sample' in config.venvs
        assert 'sample' == config.scripts['sample.py']

    def test_venv_config_scripts(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nsample.py=sample\npip=sample"})

        config.load()

        assert {'sample.py', 'pip'} <= set(config.scripts)

    def test_venv_config_venvs(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[sample]\n[pip]\n"})

        config.load()

        assert {'sample', 'pip'} <= set(config.venvs)

    def test_venv_config_ignored(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[Sample]\n[pip.Test]\n"})

        config.load()

        assert not config.venvs
        config_deps.echo.assert_called_with(StringContaining("Sample, pip.Test"))


class TestVenvConfigSearch(VenvConfigFixtures):
    def test_config_search(self, config_deps: Mock, config: VenvConfig):
        config.search_path([])

        config.load()

        config_deps.exists.assert_any_call(Path('.').absolute() / '.sv_cfg')

    def test_config_search_string(self, config_deps: Mock, config: VenvConfig):
        config.search_path(path.pathsep.join(['Test', 'Path']))

        config.load()

        config_deps.exists.assert_any_call(Path('Test').absolute() / '.sv_cfg')
        config_deps.exists.assert_any_call(Path('Path').absolute() / '.sv_cfg')

    def test_config_search_list(self, config_deps: Mock, config: VenvConfig):
        config.search_path(['Test', 'Path'])

        config.load()

        config_deps.exists.assert_any_call(Path('Test').absolute() / '.sv_cfg')
        config_deps.exists.assert_any_call(Path('Path').absolute() / '.sv_cfg')


class TestVenvConfigVerbose(VenvConfigFixtures):
    def test_verbose_default(self, config: VenvConfig):
        assert not config.verbose

    def test_verbose_set(self, config: VenvConfig):
        config.set_verbose()

        assert config.verbose

    def test_info_default(self, config_deps: Mock, config: VenvConfig):
        config.info("Test")

        config_deps.echo.assert_not_called()

    def test_info_verbose(self, config_deps: Mock, config: VenvConfig):
        config.set_verbose()

        config.info("Test")

        config_deps.echo.assert_called_once_with("Test")


class TestVenvConfigDetails(VenvConfigFixtures):
    def test_venv_prerequisites(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[sample]\nprerequisites = first\n\tsecond\n"})

        config.load()

        venv = config.venvs['sample']
        assert {'first', 'second'} == venv.prerequisites

    def test_venv_requirements(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[sample]\nrequirements = alpha\n\tbeta\n"})

        config.load()

        venv = config.venvs['sample']
        assert {'alpha', 'beta'} == venv.requirements


class TestVenvConfigLocation(VenvConfigFixtures):
    def test_venv_current(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[pip.test]\n"})

        config.load()

        assert '~' not in str(config.venvs['pip.test'])

    def test_venv_user(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.USER_sv_cfg: "[pip.test]\n"})

        config.load()

        assert path.join('~', '.sv') in str(config.venvs['pip.test'])

    def test_venv_local(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[pip.test]\nlocation = ~\n"})

        config.load()

        assert path.join('~', '.sv') in str(config.venvs['pip.test'])


class TestVenvConfigList(VenvConfigFixtures):
    def test_list_empty(self, config_deps: Mock, config: VenvConfig) -> None:
        config.list()

        config_deps.echo.assert_called_with(StringContaining("Config Paths: ["))

    def test_list_basic(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]\n"})

        config.load()
        config.list()

        config_deps.echo.assert_called_with(path.join('test (.sv', 'test) [.sv_cfg]'))

    def test_list_requirements(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]\nrequirements = second\n\tfirst\n"})
        config.load()

        config.list()

        config_deps.echo.assert_called_with("\tRequirements: first\n\t\tsecond")

    def test_list_prerequisites(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]\nprerequisites = beta\n\talpha\n"})
        config.load()

        config.list()

        config_deps.echo.assert_called_with("\tPrerequisites: alpha\n\t\tbeta")

    def test_list_scripts(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\nsample = test\ntester = test"})
        config.load()

        config.list()

        config_deps.echo.assert_called_with("\tScripts: sample, tester")


class TestVenvConfigRegister(VenvConfigFixtures):
    def test_register(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        config.register('test', ('package',))

        config_deps.echo.assert_called_with(StringContaining("Registering"))
        sv_cfg = path.abspath('.sv_cfg')
        assert sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[sv_cfg]
        assert "[test]" in out_str
        assert "requirements = package" in out_str
        assert "global" not in out_str
        assert "local" not in out_str

    def test_register_local(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        config.register('test', ('package',), config_path='$CWD')

        config_deps.echo.assert_called_with(StringContaining("Registering"))
        assert self.CWD_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.CWD_sv_cfg]
        assert "requirements = package" in out_str

    def test_register_global(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        config.register('test', ('package',), config_path='~/.config')

        config_deps.echo.assert_called_with(StringContaining("Registering"))
        assert self.USER_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.USER_sv_cfg]
        assert "requirements = package" in out_str

    def test_register_scripts(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        config.register('test', ('package1', 'package2'), config_path='Test')

        config_deps.echo.assert_called_with(StringContaining("Registering"))
        test_sv_cfg = path.expandvars(path.join('$CWD', 'Test', '.sv_cfg'))
        assert test_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[test_sv_cfg]
        assert "package1.script = test" in out_str
        assert "package2.script = test" in out_str
        assert "requirements = package1\n\tpackage2" in out_str

    def test_register_user(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {})
        config_write(config_deps)
        config_scripts(config_deps)

        config.register('test', ('package',), config_path='$CWD')

        config_deps.echo.assert_called_with(StringContaining("Registering"))
        assert self.CWD_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.CWD_sv_cfg]
        assert "[test]" in out_str
        assert "requirements = package" in out_str
        assert "global" not in out_str
        assert "local" not in out_str

    def test_register_existing(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {
            self.CWD_sv_cfg: """[SCRIPTS]\nsample = test\n\n[test]\nprerequisites = early\nrequirements = old\n"""
        })
        config_write(config_deps)
        config_scripts(config_deps)

        config.register('test', ('new',), config_path='.')

        config_deps.echo.assert_called_with(StringContaining("Registering"))
        assert self.CWD_sv_cfg in config_deps.out_str
        out_str = config_deps.out_str[self.CWD_sv_cfg]
        assert "[test]" in out_str
        assert "[SCRIPTS]" in out_str
        assert "prerequisites = early" in out_str
        assert "requirements = new\n\told" in out_str
        assert "global" not in out_str
        assert "local" not in out_str


class TestVenvConfigCreate(VenvConfigFixtures):
    def test_create_venv(self, venv_deps: Mock, config_deps: Mock, config: VenvConfig) -> None:
        venv_exists(venv_deps)
        config_read(config_deps, {self.CWD_sv_cfg: "[test]"})
        config.load()

        config.create('test')

        venv_deps.echo.assert_called_with(StringContaining("Creating venv test"))

    def test_create_script(self, venv_deps: Mock, config_deps: Mock, config: VenvConfig) -> None:
        venv_exists(venv_deps)
        config_read(config_deps, {self.CWD_sv_cfg: "[SCRIPTS]\ntester = test"})
        config.load()

        config.create('tester')

        venv_deps.echo.assert_called_with(StringContaining("Creating venv test"))

    def test_create_missing(self, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]"})
        config.load()

        config.create('other')

        config_deps.echo.assert_called_with("Unable to find venv or script other")

    def test_create_exists(self, venv_deps: Mock, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]"})
        venv_exists(venv_deps, self.CWD_sv_test)
        config.load()

        config.create('test')

        venv_deps.echo.assert_not_called()

    def test_create_clean(self, venv_deps: Mock, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]"})
        venv_exists(venv_deps, self.CWD_sv_test)
        config.load()

        config.create('test', clean=True)

        venv_deps.echo.assert_called_with(StringContaining("Cleaning venv test"))

    def test_create_update(self, venv_deps: Mock, config_deps: Mock, config: VenvConfig) -> None:
        config_read(config_deps, {self.CWD_sv_cfg: "[test]"})
        venv_exists(venv_deps, self.CWD_sv_test)
        config.load()

        config.create('test', update=True)

        venv_deps.echo.assert_called_with(StringContaining("Updating venv test"))
