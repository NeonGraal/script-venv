# -*- coding: utf-8 -*-

""" Venv tests """
import os
from random import randrange

import pytest
from typing import cast, Callable

from script_venv.venv import VEnv, VEnvDependencies
from tests.factory import TestVEnvDependencies


class VEnvFixtures(object):
    @pytest.fixture
    def deps(self) -> TestVEnvDependencies:
        return TestVEnvDependencies()

    @pytest.fixture
    def venv(self, deps: VEnvDependencies) -> VEnv:
        return VEnv('test', deps)


class TestVEnv(VEnvFixtures):
    @staticmethod
    def test_venv_str(venv: VEnv) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        deps.path_exists = False
        assert ["test (~", ".sv", "test !MISSING)"] == str(venv).split(os.sep)

        deps.path_exists = True
        assert ["test (~", ".sv", "test)"] == str(venv).split(os.sep)

    @staticmethod
    def test_venv_exists(venv: VEnv) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        deps.path_exists = False
        assert not venv.exists()

        deps.path_exists = True
        assert venv.exists()

    @staticmethod
    def test_venv_run(venv: VEnv) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        deps.ret_code = randrange(1, 200)
        deps.path_exists = False
        return_code = venv.run('test', 'arg1', 'arg2')

        assert deps.ret_code == return_code
        assert {'test', 'arg1', 'arg2'} < set(deps.run[0])
        assert 'VIRTUAL_ENV' in deps.run[1]

        deps.ret_code = randrange(1, 200)
        deps.path_exists = True
        return_code = venv.run('test', 'arg1', 'arg2')

        assert deps.ret_code == return_code
        cmd = deps.run[0].pop(0)
        assert 'test' in cmd
        assert ['arg1', 'arg2'] == deps.run[0]

    @staticmethod
    def test_venv_install(venv: VEnv) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        venv.install('package1', 'package2')

        python = deps.run[0].pop(0)
        assert 'python' in python
        assert ['-m', 'pip', 'install', 'package1', 'package2'] == deps.run[0]

    @staticmethod
    def test_venv_create(venv: VEnv,
                         click_iso: Callable) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        deps.path_exists = False
        with click_iso() as out:
            return_code = venv.create()
            click_out = out.getvalue()

        assert return_code
        assert b"Creating" in click_out
        assert ['.sv', 'test'] == deps.created[0].split(os.sep)[-2:]

    @staticmethod
    def test_venv_create_exists(venv: VEnv) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        deps.path_exists = True
        return_code = venv.create()

        assert not return_code

    @staticmethod
    def test_venv_create_clean(venv: VEnv,
                               click_iso: Callable) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        deps.path_exists = True
        with click_iso() as out:
            return_code = venv.create(clean=True)
            click_out = out.getvalue()

        assert return_code
        assert b"Cleaning" in click_out
        assert ['.sv', 'test'] == deps.created[0].split(os.sep)[-2:]

    @staticmethod
    def test_venv_create_prerequisites(venv: VEnv,
                                       click_iso: Callable) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)

        venv.prerequisites = {'alpha'}
        deps.path_exists = False
        with click_iso() as out:
            return_code = venv.create()
            click_out = out.getvalue()

        assert return_code
        assert b"Creating" in click_out
        assert ['.sv', 'test'] == deps.created[0].split(os.sep)[-2:]
        assert venv.prerequisites < set(deps.run[0])
