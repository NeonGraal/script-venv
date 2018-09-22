# -*- coding: utf-8 -*-

""" Venv tests """

from os import path
from random import randrange
from typing import cast
from unittest.mock import Mock, ANY, MagicMock

import pytest

from script_venv.venv import VEnv, VEnvDependencies, _exe, _bin

from .utils import venv_exists, StringContaining


class VEnvFixtures(object):
    CWD_sv_test = path.abspath(path.join('.sv', 'test'))

    @pytest.fixture
    def venv_deps(self) -> Mock:
        venv_mock = MagicMock(spec=VEnvDependencies, name="venv_deps")
        venv_exists(venv_mock, self.CWD_sv_test)
        return venv_mock

    @pytest.fixture
    def venv(self, venv_deps: VEnvDependencies) -> VEnv:
        return VEnv('test', venv_deps, '.')


class TestVEnv(VEnvFixtures):
    def test_venv_location(self, venv_deps: Mock) -> None:
        venv = VEnv('test', cast(VEnvDependencies, venv_deps), 'TEST', location='test')

        expected = path.join("test (TEST", "test", ".sv", "test !MISSING) [TEST", ".sv_cfg]")
        assert expected == str(venv)
        assert venv_deps.exists.called

    def test_venv_str(self, venv_deps: Mock, venv: VEnv) -> None:
        expected = path.join("test (.sv", "test) [.sv_cfg]")
        assert expected == str(venv)
        assert venv_deps.exists.called

    def test_venv_exists(self, venv_deps: Mock, venv: VEnv) -> None:
        assert venv.exists()
        assert venv_deps.exists.called

    def test_venv_run_cmd(self, venv_deps: Mock, venv: VEnv) -> None:
        venv_exists(venv_deps, self.CWD_sv_test, path.join(self.CWD_sv_test, _bin, 'test' + _exe))
        expected_ret_code = randrange(1, 200)
        venv_deps.runner.return_value = expected_ret_code

        return_code = venv.run('test', 'arg1', 'arg2')

        assert expected_ret_code == return_code
        venv_deps.runner.assert_called_once_with([ANY, 'arg1', 'arg2'], env=dict(PATH=ANY, VIRTUAL_ENV=ANY))

    def test_venv_run_python(self, venv_deps: Mock, venv: VEnv) -> None:
        expected_ret_code = randrange(1, 200)
        venv_deps.runner.return_value = expected_ret_code
        venv_deps.exists.return_value = False

        return_code = venv.run('test', 'arg1', 'arg2')

        assert expected_ret_code == return_code
        venv_deps.runner.assert_called_once_with([ANY, 'test', 'arg1', 'arg2'], env=dict(PATH=ANY, VIRTUAL_ENV=ANY))

    def test_venv_install(self, venv_deps: Mock, venv: VEnv) -> None:
        venv.install('package1', 'package2')

        venv_deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', 'package1', 'package2'], env=ANY)


class TestVEnvCreate(VEnvFixtures):
    def test_venv_create(self, venv_deps: Mock, venv: VEnv) -> None:
        venv_exists(venv_deps)

        return_code = venv.create()

        assert return_code
        venv_deps.echo.assert_called_once_with(StringContaining("Creating"))
        venv_deps.creator.assert_called_once_with(ANY, clear=False)

    def test_venv_create_exists(self, venv: VEnv) -> None:
        return_code = venv.create()

        assert not return_code

    def test_venv_create_clean(self, venv_deps: Mock, venv: VEnv) -> None:
        return_code = venv.create(clean=True)

        assert return_code
        venv_deps.echo.assert_called_once_with(StringContaining("Cleaning"))
        venv_deps.creator.assert_called_once_with(ANY, clear=True)

    def test_venv_create_update(self, venv_deps: Mock, venv: VEnv) -> None:
        return_code = venv.create(update=True)

        assert return_code
        venv_deps.echo.assert_called_once_with(StringContaining("Updating"))
        venv_deps.creator.assert_called_once_with(ANY, clear=False)
        venv_deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', '-U', 'pip', 'wheel'], env=ANY)

    def test_venv_create_prerequisites(self, venv_deps: Mock, venv: VEnv) -> None:
        venv_exists(venv_deps)
        venv.prerequisites = {'alpha'}

        return_code = venv.create()

        assert return_code
        venv_deps.echo.assert_called_once_with(StringContaining("Creating"))
        venv_deps.creator.assert_called_once_with(ANY, clear=False)
        venv_deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', 'alpha'], env=ANY)
