# -*- coding: utf-8 -*-

""" Config file processing """

import click
from click import echo
from configparser import ConfigParser
import os
from pathlib2 import Path
import subprocess
from sys import version_info, platform
from typing import Iterable, Tuple, Dict, Any, IO, Mapping  # noqa: F401
import venv

from .config import ConfigDependencies
from .venv import VEnv, VEnvDependencies


class ConfigDependenciesImpl(ConfigDependencies):  # pragma: no cover
    def venv_deps(self) -> VEnvDependencies:
        return VEnvDependenciesImpl()

    def echo(self, msg: str):
        click.echo(msg)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def read(self, path: Path) -> IO[Any]:
        return path.open()

    def scripts(self, venv: VEnv, packages: Iterable[str]) -> Iterable[Tuple[str, str]]:
        if venv.create(update=True):
            if venv.requirements:
                venv.install(*venv.requirements)
        venv.install(*packages)

        try:
            import pkg_resources
        except ImportError:
            echo("Unable to import pkg_resources to register %s into %s" % (sorted(packages), venv))
            return []

        if platform == 'win32':
            libpath = venv.abs_path / 'lib' / 'site-packages'
        else:
            ver_path = 'python%d.%d' % version_info[:2]
            libpath = venv.abs_path / 'lib' / ver_path

        pkg_env = pkg_resources.Environment(search_path=[str(libpath / 'site-packages')])

        def pkg_scripts(p: str) -> Iterable[str]:
            scripts = {}  # type: Dict
            dist = pkg_env[p]
            if len(dist):
                scripts = dist[0].get_entry_map().get('console_scripts') or {}
            return scripts.keys()

        return ((s, p) for p in packages for s in pkg_scripts(p))

    def write(self, config: ConfigParser, path: Path):
        with path.open('w') as out_config:
            config.write(out_config)


class VEnvDependenciesImpl(VEnvDependencies):  # pragma: no cover
    def creator(self, path: Path, clear: bool = False) -> None:
        venv.create(str(path), with_pip=True, clear=clear)

    def echo(self, msg: str):
        click.echo(msg)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def runner(self, cmd: Iterable[str], env: Mapping[str, str] = None) -> int:
        new_env = dict(os.environ)  # type: Dict[str, str]
        if env:
            new_env.update(env)

        return subprocess.call(list(cmd), env=new_env)
