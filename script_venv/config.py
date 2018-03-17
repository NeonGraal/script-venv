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

SCRIPTS = "SCRIPTS"


class VenvConfig(object):
    def __init__(self):
        self._venvs = {}

    def load(self, config_path: Path):
        config_file = config_path / '.sv_cfg'

        if config_file.exists():
            config = ConfigParser()
            config.read(config_file)

            scripts = config[SCRIPTS]
            for s in scripts:
                v = scripts[s] or s
                self._venvs[s] = VEnv(v, local=True)

    def scripts(self):
        return self._venvs.keys()

    def venvs(self):
        return self._venvs.values()

    def __getitem__(self, item):
        return self._venvs[item]


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
