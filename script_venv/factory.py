# -*- coding: utf-8 -*-

""" Config file processing """
import venv

from click import echo
from configparser import ConfigParser
import os
from pathlib import Path
import subprocess
from typing import Iterable, Tuple, Dict, Any, IO  # noqa: F401

from .config import ConfigDependencies
from .venv import VEnv, VEnvDependencies


class ConfigDependenciesImpl(ConfigDependencies):
    def venv_deps(self) -> VEnvDependencies:
        return VEnvDependenciesImpl()

    def exists(self, path: Path) -> bool:
        return path.exists()

    def read(self, path: Path) -> IO[Any]:  # pragma: no cover
        return path.open()

    def scripts(self, venv: VEnv, packages: Iterable[str]) -> Iterable[Tuple[str, str]]:  # pragma: no cover
        if venv.create():
            venv.install(*venv.requirements)
        venv.install(*packages)

        try:
            import pkg_resources
        except ImportError:
            echo("Unable to import pkg_resources to register %s into %s" % (sorted(packages), venv))
            return []

        pkg_env = pkg_resources.Environment(search_path=[str(venv.abs_path / 'lib' / 'site-packages')])

        def pkg_scripts(p: str) -> Iterable[str]:
            scripts = {}  # type: Dict
            dist = pkg_env[p]
            if len(dist):
                scripts = dist[0].get_entry_map().get('console_scripts') or {}
            return scripts.keys()

        return ((s, p) for p in packages for s in pkg_scripts(p))

    def write(self, config: ConfigParser, path: Path):  # pragma: no cover
        with path.open('w') as out_config:
            config.write(out_config)


class VEnvDependenciesImpl(VEnvDependencies):  # pragma: no cover
    def creator(self, path: Path, clear: bool = False) -> None:
        venv.create(str(path), with_pip=True, clear=clear)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def runner(self, cmd: Iterable[str], env: Dict[str, str] = None) -> int:
        new_env = dict(os.environ)  # type: Dict[str, str]
        new_env.update(env)

        return subprocess.call(list(cmd), env=new_env)
