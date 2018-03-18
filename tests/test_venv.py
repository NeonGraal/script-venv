# -*- coding: utf-8 -*-

""" Venv tests """
import os
import pytest
from random import randrange
from script_venv.venv import VEnv


@pytest.fixture
def venv():
    return VEnv('test')


def test_venv_str(venv) -> None:
    assert "test" in str(venv)


def test_venv_exists(venv) -> None:
    assert not venv.exists()


def test_venv_run(venv) -> None:
    result = {}
    expected_code = randrange(1, 200)

    def test_runner(args, env=None):
        result['args'] = args
        result['env'] = env

        return expected_code

    return_code = venv.run('test', ['arg1', 'arg2'], runner=test_runner)

    assert expected_code == return_code
    assert {'test', 'arg1', 'arg2'} < set(result['args'])
    assert 'VIRTUAL_ENV' in result['env']


def test_venv_create_no_req(venv) -> None:
    result = {}

    def test_creator(path, with_pip=True):
        result['path'] = path
        result['with_pip'] = with_pip

    return_code = venv.create(creator=test_creator)

    assert not return_code


def test_venv_create_req(venv) -> None:
    result = {}

    def test_creator(path, with_pip=True):
        result['path'] = path
        result['with_pip'] = with_pip

    venv.requirements = ['alpha']
    return_code = venv.create(creator=test_creator)

    assert return_code
    assert ['.sv', 'test'] == result['path'].split(os.sep)[-2:]
    assert result['with_pip']
