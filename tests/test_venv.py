# -*- coding: utf-8 -*-

""" Venv tests """
import os
from random import randrange
from typing import cast, Callable
from unittest.mock import Mock, ANY

import pytest

from script_venv.venv import VEnv, VEnvDependencies


class VEnvFixtures(object):
    @pytest.fixture
    def deps(self) -> VEnvDependencies:
        return cast(VEnvDependencies, Mock(spec=VEnvDependencies))

    @pytest.fixture
    def venv(self, deps: VEnvDependencies) -> VEnv:
        return VEnv('test', deps)


class TestVEnv(VEnvFixtures):
    @staticmethod
    def test_venv_str(venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        expected = os.sep.join(["test (~", ".sv", "test)"])
        assert expected == str(venv)
        assert deps.exists.called

    @staticmethod
    def test_venv_exists(venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        assert venv.exists()
        assert deps.exists.called

    @staticmethod
    def test_venv_run_cmd(venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        expected_ret_code = randrange(1, 200)
        deps.runner.return_value = expected_ret_code
        deps.exists.return_value = True

        return_code = venv.run('test', 'arg1', 'arg2')

        assert expected_ret_code == return_code
        deps.runner.assert_called_once_with([ANY, 'arg1', 'arg2'], env=dict(PATH=ANY, VIRTUAL_ENV=ANY))

    @staticmethod
    def test_venv_run_python(venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        expected_ret_code = randrange(1, 200)
        deps.runner.return_value = expected_ret_code
        deps.exists.return_value = False

        return_code = venv.run('test', 'arg1', 'arg2')

        assert expected_ret_code == return_code
        deps.runner.assert_called_once_with([ANY, 'test', 'arg1', 'arg2'], env=dict(PATH=ANY, VIRTUAL_ENV=ANY))

    @staticmethod
    def test_venv_install(venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)

        venv.install('package1', 'package2')

        deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', 'package1', 'package2'], env=ANY)


class TestVEnvCreate(VEnvFixtures):
    @staticmethod
    def test_venv_create(venv: VEnv,
                         click_iso: Callable) -> None:
        deps = cast(Mock, venv.deps)
        deps.exists.return_value = False

        with click_iso() as out:
            return_code = venv.create()
            click_out = out.getvalue()

        assert return_code
        assert b"Creating" in click_out
        deps.creator.assert_called_once_with(ANY, clear=False)

    @staticmethod
    def test_venv_create_exists(venv: VEnv) -> None:
        deps = cast(Mock, venv.deps)
        deps.exists.return_value = True

        return_code = venv.create()

        assert not return_code

    @staticmethod
    def test_venv_create_clean(venv: VEnv,
                               click_iso: Callable) -> None:
        deps = cast(Mock, venv.deps)
        deps.exists.return_value = True

        with click_iso() as out:
            return_code = venv.create(clean=True)
            click_out = out.getvalue()

        assert return_code
        assert b"Cleaning" in click_out
        deps.creator.assert_called_once_with(ANY, clear=True)

    @staticmethod
    def test_venv_create_update(venv: VEnv,
                                click_iso: Callable) -> None:
        deps = cast(Mock, venv.deps)
        deps.exists.return_value = True

        with click_iso() as out:
            return_code = venv.create(update=True)
            click_out = out.getvalue()

        assert return_code
        assert b"Updating" in click_out
        deps.creator.assert_called_once_with(ANY, clear=False)
        deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', '-U', 'pip'], env=ANY)

    @staticmethod
    def test_venv_create_prerequisites(venv: VEnv,
                                       click_iso: Callable) -> None:
        deps = cast(Mock, venv.deps)
        deps.exists.return_value = False
        venv.prerequisites = {'alpha'}

        with click_iso() as out:
            return_code = venv.create()
            click_out = out.getvalue()

        assert return_code
        assert b"Creating" in click_out
        deps.creator.assert_called_once_with(ANY, clear=False)
        deps.runner.assert_called_once_with([ANY, '-m', 'pip', 'install', 'alpha'], env=ANY)
