# -*- coding: utf-8 -*-

""" Venv tests """
import os
from random import randrange

import pytest
from typing import cast

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
        assert "test" in str(venv)

    @staticmethod
    def test_venv_exists(venv: VEnv) -> None:
        assert not venv.exists()

    @staticmethod
    def test_venv_run(venv: VEnv) -> None:
        deps = cast(TestVEnvDependencies, venv.deps)
        deps.ret_code = randrange(1, 200)

        return_code = venv.run('test', 'arg1', 'arg2')

        assert deps.ret_code == return_code
        assert {'test', 'arg1', 'arg2'} < set(deps.run[0])
        assert 'VIRTUAL_ENV' in deps.run[1]

    @staticmethod
    def test_venv_create_req(venv) -> None:
        venv.requirements = ['alpha']

        return_code = venv.create()

        deps = cast(TestVEnvDependencies, venv.deps)
        assert return_code
        assert ['.sv', 'test'] == deps.created[0].split(os.sep)[-2:]
