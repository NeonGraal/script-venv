# -*- coding: utf-8 -*-

""" Venv tests """
from os import path
from random import randrange
from typing import cast, Callable
from unittest.mock import Mock, ANY, MagicMock

import pytest

from script_venv.venv import VEnv, VEnvDependencies, _exe, _bin
from tests.utils import venv_exists


class VEnvFixtures(object):
    TEST_sv_test = path.abspath(path.join('TEST', '.sv', 'test'))

    @pytest.fixture
    def venv_deps(self) -> VEnvDependencies:
        venv_mock = MagicMock(spec=VEnvDependencies, name="venv_deps")
        venv_exists(venv_mock, self.TEST_sv_test)
        return cast(VEnvDependencies, venv_mock)

    @pytest.fixture
    def venv(self, venv_deps: VEnvDependencies) -> VEnv:
        return VEnv('test', venv_deps, 'TEST')


class TestVEnv(VEnvFixtures):
    def test_venv_location(self, venv_deps: VEnvDependencies) -> None:
        venv = VEnv('test', venv_deps, 'TEST', location='test')
        deps_mock = cast(Mock, venv_deps)
        expected = path.join("test (TEST", "test", ".sv", "test !MISSING) [TEST", ".sv_cfg]")
        assert expected == str(venv)
        assert deps_mock.exists.called

    def test_venv_str(self, venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)
        expected = path.join("test (TEST", ".sv", "test) [TEST", '.sv_cfg]')
        assert expected == str(venv)
        assert deps.exists.called

    def test_venv_exists(self, venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        assert venv.exists()
        assert deps.exists.called

    def test_venv_run_cmd(self, venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)
        venv_exists(deps, self.TEST_sv_test, path.join(self.TEST_sv_test, _bin, 'test' + _exe))
        expected_ret_code = randrange(1, 200)
        deps.runner.return_value = expected_ret_code

        return_code = venv.run('test', 'arg1', 'arg2')

        assert expected_ret_code == return_code
        deps.runner.assert_called_once_with([ANY, 'arg1', 'arg2'], env=dict(PATH=ANY, VIRTUAL_ENV=ANY))

    def test_venv_run_python(self, venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        expected_ret_code = randrange(1, 200)
        deps.runner.return_value = expected_ret_code
        deps.exists.return_value = False

        return_code = venv.run('test', 'arg1', 'arg2')

        assert expected_ret_code == return_code
        deps.runner.assert_called_once_with([ANY, 'test', 'arg1', 'arg2'], env=dict(PATH=ANY, VIRTUAL_ENV=ANY))

    def test_venv_install(self, venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        venv.install('package1', 'package2')

        deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', 'package1', 'package2'], env=ANY)


class TestVEnvCreate(VEnvFixtures):
    def test_venv_create(self, venv: VEnv,
                         click_iso: Callable) -> None:
        deps = cast(Mock, venv.deps)
        venv_exists(deps)

        with click_iso() as out:
            return_code = venv.create()
            click_out = out.getvalue()

        assert return_code
        assert b"Creating" in click_out
        deps.creator.assert_called_once_with(ANY, clear=False)

    def test_venv_create_exists(self, venv: VEnv) -> None:
        return_code = venv.create()

        assert not return_code

    def test_venv_create_clean(self,
                               venv: VEnv,
                               click_iso: Callable) -> None:
        with click_iso() as out:
            return_code = venv.create(clean=True)
            click_out = out.getvalue()

        assert return_code
        assert b"Cleaning" in click_out
        deps = cast(Mock, venv.deps)
        deps.creator.assert_called_once_with(ANY, clear=True)

    def test_venv_create_update(self,
                                venv: VEnv,
                                click_iso: Callable) -> None:
        with click_iso() as out:
            return_code = venv.create(update=True)
            click_out = out.getvalue()

        assert return_code
        assert b"Updating" in click_out
        deps = cast(Mock, venv.deps)
        deps.creator.assert_called_once_with(ANY, clear=False)
        deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', '-U', 'pip'], env=ANY)

    def test_venv_create_prerequisites(self,
                                       venv: VEnv,
                                       click_iso: Callable) -> None:
        deps = cast(Mock, venv.deps)
        venv_exists(deps)
        venv.prerequisites = {'alpha'}

        with click_iso() as out:
            return_code = venv.create()
            click_out = out.getvalue()

        assert return_code
        assert b"Creating" in click_out
        deps.creator.assert_called_once_with(ANY, clear=False)
        deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', 'alpha'], env=ANY)
