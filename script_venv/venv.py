# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
from pathlib import Path
from typing import Iterable

import sys

_r = 'requirements'

if os.name == 'nt':
    _bin = 'Scripts'
else:
    _bin = 'bin'


class VEnv(object):
    def __init__(self, name, requirements: Iterable[str]=None, local=False):
        self.name = name
        self.requirements = requirements
        self.base_path = (Path.cwd() if local else Path.home())
        self.prefix = '' if local else '~/'
        self.env_path =  Path('.sv') / name

    def __str__(self):
        return "%(name)s (%(prefix)s%(env_path)s)" % self.__dict__

    def run(self, cmd, args):
        bin_path = self.base_path / self.env_path / _bin
        cmd_path = bin_path / cmd
        if cmd_path.exists():
            print(cmd_path, args)
        else:
            print(bin_path / os.path.basename(sys.executable), cmd, args)
