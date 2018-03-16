# -*- coding: utf-8 -*-

""" Config file processing """
from configparser import ConfigParser
from pathlib import Path

from .venv import VEnv

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
VENVS = {}

local_config = Path.cwd() / '.sv_cfg'

if local_config.exists():
    config = ConfigParser()
    config.read(local_config)

    scripts = config[_SCRIPTS]
    for s in scripts:
        v = scripts[s] or s
        VENVS[s] = VEnv(v, local=True)

"""
user_config = path.expanduser('~/.sv_cfg')
if path.isfile(user_config):
    config = ConfigParser()
    config.read(user_config)

    for v in config.sections():
        if v.islower():
            requirements = [r for r in config.get(v, 'requirements').splitlines() if r]
            _VENVS[v] = VEnv(v, requirements=requirements, local=config.getboolean(v, 'local', False))

    scripts = config['SCRIPTS']
    for s in scripts:
        if scripts[s] in _VENVS:
            _SCRIPTS[s] = _VENVS[scripts[s]]
"""
