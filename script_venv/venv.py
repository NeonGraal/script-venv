# -*- coding: utf-8 -*-

"""Virtual environment handling"""

import os
import sys
from pathlib2 import Path
from typing import Iterable, Dict  # noqa: F401

_r = 'requirements'

if os.name == 'nt':  # pragma: no cover
    _bin = 'Scripts'
    _exe = '.exe'
    _quote = '"%s"'
else:  # pragma: no cover
    _bin = 'bin'
    _exe = ''
    _quote = '%s'

_CWD = os.getcwd()
os.environ['CWD'] = _CWD


def abs_path(raw_path: Path) -> Path:
    str_path = str(raw_path)
    usr_path = os.path.expandvars(str_path)
    abs_path = Path(usr_path).expanduser()
    return abs_path.absolute()


def venv_path(cfg_path: Path, location: str = None) -> Path:
    if cfg_path.name == '.config':
        cfg_path = Path(*cfg_path.parts[:-1])
    return cfg_path / location if location else cfg_path


class VEnvDependencies(object):  # pragma: no cover
    def echo(self, msg: str):
        raise NotImplementedError()

    def exists(self, path: Path) -> bool:
        raise NotImplementedError()

    def runner(self, cmd: Iterable[str], env: Dict[str, str] = None) -> int:
        raise NotImplementedError()

    def creator(self, path: Path, clear: bool = False) -> None:
        raise NotImplementedError()


class VEnv(object):
    def __init__(self, name: str, deps: VEnvDependencies,
                 config_path: str,
                 requirements: Iterable[str] = None,
                 prerequisites: Iterable[str] = None,
                 location: str = None) -> None:
        self.name = name
        self.deps = deps
        self.config_path = config_path
        self.requirements = set(requirements or [])
        self.prerequisites = set(prerequisites or [])
        self.env_path = venv_path(Path(config_path), location) / '.sv' / name
        self.abs_path = abs_path(self.env_path)

    def __str__(self) -> str:
        return "%s (%s%s) [%s]" % (self.name, self.env_path,
                                   '' if self.exists() else ' !MISSING',
                                   Path(self.config_path) / '.sv_cfg')

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

    def create(self, clean: bool = False, update: bool = False) -> bool:
        if self.exists():
            if clean:
                action = "Cleaning"
            elif update:
                action = "Updating"
            else:
                return False
        else:
            action = "Creating"
        self.deps.echo("%s venv %s at %s" % (action, self.name, self.env_path))

        self.deps.creator(self.abs_path, clear=clean)
        install_params = (['-U', 'pip', 'wheel'] if update else []) + list(sorted(self.prerequisites))
        if install_params:
            self.install(*install_params)
        return True
