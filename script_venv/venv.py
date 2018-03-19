# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable, List, Dict  # noqa: F401
import venv


_r = 'requirements'

if os.name == 'nt':  # pragma: no cover
    _bin = 'Scripts'
    _exe = '.exe'
    _quote = '"%s"'
else:  # pragma: no cover
    _bin = 'bin'
    _exe = ''
    _quote = '%s'


class VEnv(object):
    def __init__(self, name, requirements: Iterable[str] = None, local=False) -> None:
        self.name = name
        self.requirements = requirements
        self.env_path = str((Path('.sv') if local else Path('~') / '.sv') / name)
        self.abs_path = Path(os.path.expanduser(self.env_path)).absolute()

    def __str__(self) -> str:
        return "%s (%s%s)" % (self.name, self.env_path, '' if self.exists() else ' !MISSING')

    def exists(self) -> bool:
        return self.abs_path.exists()

    def run(self, cmd_name: str, args: List[str], runner=None) -> int:
        runner = runner if callable(runner) else subprocess.call

        bin_path = self.abs_path / _bin
        cmd_path = bin_path / (cmd_name + _exe)
        new_env = dict()  # type: Dict[str,str]
        new_env.update(os.environ,
                       VIRTUAL_ENV=str(self.abs_path),
                       PATH=''.join([_quote % self.abs_path, os.pathsep, os.environ['PATH']])
                       )
        if cmd_path.exists():  # pragma: no cover
            cmd = [str(cmd_path)]
        else:
            cmd = [str(bin_path / os.path.basename(sys.executable)), cmd_name]

        return runner(cmd + args, env=new_env)

    def create(self, creator=None) -> bool:
        if not self.requirements:
            return False

        creator = creator if callable(creator) else venv.create

        creator(str(self.abs_path), with_pip=True)
        return True
