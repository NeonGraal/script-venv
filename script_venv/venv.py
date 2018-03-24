# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
import sys
from pathlib import Path
from typing import Iterable, Dict  # noqa: F401

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


class VEnvDependencies(object):  # pragma: no cover
    def exists(self, path: Path) -> bool:
        raise NotImplementedError()

    def runner(self, cmd: Iterable[str], env: Dict[str, str] = None) -> int:
        raise NotImplementedError()

    def creator(self, path: Path, clear: bool = False) -> None:
        raise NotImplementedError()


class VEnv(object):
    def __init__(self, name, deps: VEnvDependencies,
                 requirements: Iterable[str] = None,
                 prerequisites: Iterable[str] = None,
                 local=False) -> None:
        self.name = name
        self.deps = deps
        self.requirements = set(requirements or [])
        self.prerequisites = set(prerequisites or [])
        self.env_path = str((Path('.sv') if local else Path('~') / '.sv') / name)
        self.abs_path = Path(os.path.expanduser(self.env_path)).absolute()

    def __str__(self) -> str:
        return "%s (%s%s)" % (self.name, self.env_path, '' if self.exists() else ' !MISSING')

    def exists(self) -> bool:
        return self.deps.exists(self.abs_path)

    def _run_env(self) -> Dict[str, str]:
        new_env = dict(
            VIRTUAL_ENV=str(self.abs_path),
            PATH=''.join([_quote % self.abs_path, os.pathsep, os.environ['PATH']])
        )
        return new_env

    def run(self, cmd_name: str, *args: str) -> int:
        bin_path = self.abs_path / _bin
        cmd_path = bin_path / (cmd_name + _exe)
        if self.deps.exists(cmd_path):
            cmd = [str(cmd_path)]
        else:
            cmd = [str(bin_path / os.path.basename(sys.executable)), cmd_name]

        return self.deps.runner(cmd + list(args), env=self._run_env())

    def install(self, *install_args: str):
        python_path = str(self.abs_path / _bin / os.path.basename(sys.executable))
        install_cmd = [python_path, '-m', 'pip', 'install'] + list(install_args)

        return self.deps.runner(install_cmd, env=self._run_env())

    def create(self, clean=False) -> bool:
        if self.exists():
            if not clean:
                return False
            echo("Cleaning venv %s at %s" % (self.name, self.env_path))
        else:
            echo("Creating venv %s at %s" % (self.name, self.env_path))

        self.deps.creator(self.abs_path, clear=clean)
        if self.prerequisites:
            self.install(*self.prerequisites)
        return True
