# -*- coding: utf-8 -*-

""" Venv tests """
import os
import pytest
from random import randrange
from script_venv.venv import VEnv
from typing import Dict, Any


@pytest.fixture
def venv() -> VEnv:
    return VEnv('test')


def test_venv_str(venv: VEnv) -> None:
    assert "test" in str(venv)


def test_venv_exists(venv: VEnv) -> None:
    assert not venv.exists()


def test_venv_run(venv: VEnv) -> None:
    result = {}
    expected_code = randrange(1, 200)

    def test_runner(args, env=None):
        result['args'] = args
        result['env'] = env

        return expected_code

    return_code = venv.run('test', 'arg1', 'arg2', runner=test_runner)

    assert expected_code == return_code
    assert {'test', 'arg1', 'arg2'} < set(result['args'])
    assert 'VIRTUAL_ENV' in result['env']


def _make_creator(result: Dict[str, Any]):
    def test_creator(path, clear=False, with_pip=True):
        result['path'] = path
        result['with_pip'] = with_pip
        result['clear'] = clear
    return test_creator


def test_venv_create_req(venv) -> None:
    result = {}  # type: Dict[str, Any]

    venv.requirements = ['alpha']
    return_code = venv.create(creator=_make_creator(result))

    assert return_code
    assert ['.sv', 'test'] == result['path'].split(os.sep)[-2:]
    assert result['with_pip']
