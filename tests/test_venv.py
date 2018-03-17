# -*- coding: utf-8 -*-

""" Venv tests """

from script_venv.venv import VEnv


def test_venv_str() -> None:
    venv = VEnv('test')
    assert "test" in str(venv)
