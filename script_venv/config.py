# -*- coding: utf-8 -*-

""" Config file processing """
from configparser import ConfigParser
from pathlib import Path
from types import MappingProxyType

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
        self.cfgs = set()
        self._scripts = {}
        self._venvs = {}
        self._scripts_proxy = MappingProxyType(self._scripts)
        self._venvs_proxy = MappingProxyType(self._venvs)

    def load(self, config_path: Path, local: bool):
        config_file = config_path / '.sv_cfg'
        config_file_path = config_file.expanduser().absolute()

        if config_file_path.exists():
            self.cfgs.add(config_file.as_posix())
            config = ConfigParser()
            config.read_file(config_file_path.open())

            scripts = config[SCRIPTS]
            for s in scripts:
                v = scripts[s] or s
                self._scripts[s] = v
                self._venvs.setdefault(v, VEnv(v, local=local))

    @property
    def scripts(self):
        return self._scripts_proxy

    @property
    def venvs(self):
        return self._venvs_proxy
