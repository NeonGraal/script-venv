# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable

_r = 'requirements'

if os.name == 'nt':  # pragma: no cover
    _bin = 'Scripts'
    _exe = '.exe'

    def path_quote(p):
        return '"%s"' % p
else:  # pragma: no cover
    _bin = 'bin'
    _exe = ''

    def path_quote(p):
        return str(p)


class VEnv(object):
    def __init__(self, name, requirements: Iterable[str] = None, local=False) -> None:
        self.name = name
        self.requirements = requirements
        self.env_path = (Path('.sv') if local else Path('~') / '.sv') / name

    def __str__(self):
        env_path = self.env_path.expanduser().absolute()
        return "%s (%s%s)" % (self.name, self.env_path, '' if env_path.exists() else ' !MISSING')

    def run(self, cmd_name, args):
        env_path = self.env_path.expanduser().absolute()
        bin_path = env_path / _bin
        cmd_path = bin_path / (cmd_name + _exe)
        new_env = dict()
        new_env.update(os.environ,
                       VIRTUAL_ENV=str(env_path),
                       PATH=''.join([path_quote(env_path), os.pathsep, os.environ['PATH']])
                       )
        if cmd_path.exists():
            cmd = [str(cmd_path)]
        else:
            cmd = [str(bin_path / os.path.basename(sys.executable)), cmd_name]

        exit(subprocess.call(cmd + args, env=new_env))
