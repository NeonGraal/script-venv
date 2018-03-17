# -*- coding: utf-8 -*-

""" Venv tests """
from random import randrange

import pytest
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

    def to_call(args, env=None):
        result['args'] = args
        result['env'] = env

        return expected_code

    return_code = venv.run('test', ['arg1', 'arg2'], call=to_call)

    assert expected_code == return_code
    assert {'test', 'arg1', 'arg2'} < set(result['args'])
    assert 'VIRTUAL_ENV' in result['env']
