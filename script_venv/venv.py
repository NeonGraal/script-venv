# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable, List, Dict  # noqa: F401
import venv

from click import echo

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
    def __init__(self, name,
                 requirements: Iterable[str] = None,
                 prerequisites: Iterable[str] = None,
                 local=False) -> None:
        self.name = name
        self.requirements = set(requirements or [])
        self.prerequisites = set(prerequisites or [])
        self.env_path = str((Path('.sv') if local else Path('~') / '.sv') / name)
        self.abs_path = Path(os.path.expanduser(self.env_path)).absolute()

    def __str__(self) -> str:
        return "%s (%s%s)" % (self.name, self.env_path, '' if self.exists() else ' !MISSING')

    def exists(self) -> bool:
        return self.abs_path.exists()

    def _run_env(self) -> Dict[str, str]:
        new_env = dict()  # type: Dict[str, str]
        new_env.update(os.environ,
                       VIRTUAL_ENV=str(self.abs_path),
                       PATH=''.join([_quote % self.abs_path, os.pathsep, os.environ['PATH']])
                       )
        return new_env

    def run(self, cmd_name: str, *args: str, runner=None) -> int:
        runner = runner if callable(runner) else subprocess.call

        bin_path = self.abs_path / _bin
        cmd_path = bin_path / (cmd_name + _exe)
        if cmd_path.exists():  # pragma: no cover
            cmd = [str(cmd_path)]
        else:
            cmd = [str(bin_path / os.path.basename(sys.executable)), cmd_name]

        return runner(cmd + list(args), env=self._run_env())

    def install(self, *install_args: str, runner=None):
        runner = runner if callable(runner) else subprocess.call

        python_path = str(self.abs_path / _bin / os.path.basename(sys.executable))
        install_cmd = [python_path, '-m', 'pip', 'install'] + list(install_args)

        return runner(install_cmd, env=self._run_env())

    def create(self, clean=False, creator=None) -> bool:
        if self.exists():
            if not clean:
                return False
            echo("Cleaning venv %s at %s" % (self.name, self.env_path))
        else:
            echo("Creating venv %s at %s" % (self.name, self.env_path))
        creator = creator if callable(creator) else venv.create

        creator(str(self.abs_path), with_pip=True, clear=clean)
        if self.prerequisites:
            self.install(*self.prerequisites)
        return True
