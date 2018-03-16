# -*- coding: utf-8 -*-

"""Virtual environment handling"""
from pathlib import Path
from typing import Iterable

from os import path

_r = 'requirements'


class VEnv(object):
    def __init__(self, name, requirements: Iterable[str], local=False):
        self.name = name
        self.requirements = requirements
        self.env_path = Path.cwd() if local else Path.home() / '.sv' / name

    def __str__(self):
        return f"{self.name}({self.env_path})"

    def scripts(self) -> Iterable[str]:
        """ Returns a list of all scripts defined by the requirements of this VEnv"""
        return []
