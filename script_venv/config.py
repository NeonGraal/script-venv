# -*- coding: utf-8 -*-

""" Config file processing """
from configparser import ConfigParser

from os import path

from .env import VEnv

"""
Config file structure:
[SCRIPTS]
cookiecutter=cc
[PACKAGES]
jupyter
[cc]
requirements:
    cookiecutter
    pipdeptree
"""

_SCRIPTS = "SCRIPTS"
_VENVS = {}

user_config = path.expanduser('~/.sv_cfg')
if path.isfile(user_config):
    config = ConfigParser()
    config.read(user_config)

    for v in config.sections():
        if v.islower():
            requirements = [r for r in config.get(v, 'requirements').splitlines() if r]
            _VENVS[v] = VEnv(v, requirements=requirements, local=config.getboolean(v, 'local', False))

    packages = config['PACKAGES']
    for p in packages:
        v = packages[p] or p
        if v not in _VENVS:
            env = VEnv(v, requirements=p, local=False)
        else:
            env = _VENVS[v]

        for s in env.scripts():
            _SCRIPTS[s] = env

    scripts = config['SCRIPTS']
    for s in scripts:
        if scripts[s] in _VENVS:
            _SCRIPTS[s] = _VENVS[scripts[s]]
