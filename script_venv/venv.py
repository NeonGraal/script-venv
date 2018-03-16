# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
from pathlib import Path
from typing import Iterable

import sys

_r = 'requirements'

if os.name == 'nt':
    _bin = 'Scripts'


class VEnv(object):
    def __init__(self, name, requirements: Iterable[str]=None, local=False):
        self.name = name
        self.requirements = requirements
        self.env_path = (Path.cwd() if local else Path.home()) / '.sv' / name

    def __str__(self):
        return f"{self.name}({self.env_path})"

    def run(self, cmd, args):
        bin_path = self.env_path / ('Scripts' if os.name == 'nt' else 'bin')
        cmd_path = bin_path / cmd
        if cmd_path.exists():
            print(cmd_path, args)
        else:
            print(bin_path / os.path.basename(sys.executable), cmd, args)
