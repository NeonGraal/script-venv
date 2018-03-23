# -*- coding: utf-8 -*-

""" Config file processing """

from click import echo
from configparser import ConfigParser
from pathlib import Path
from typing import Iterable, Tuple, Dict, Any, IO  # noqa: F401

from .config import ConfigDependencies
from .venv import VEnv


class ConfigDependenciesImpl(ConfigDependencies):
    def write(self, config: ConfigParser, path: Path):  # pragma: no cover
        with path.open('w') as out_config:
            config.write(out_config)

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

    def read(self, path: Path) -> IO[Any]:
        return path.open()

    def exists(self, path: Path) -> bool:
        return path.exists()
