# -*- coding: utf-8 -*-

""" Config file processing """
from configparser import ConfigParser
from click import echo
from io import StringIO
from os import path
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Set, Dict, Iterable, Tuple  # noqa: F401

from .venv import VEnv

# noinspection SpellCheckingInspection
"""
Config file structure:
[SCRIPTS]
cookiecutter=cc
[PACKAGES]
jupyter
[cc]
requirements:
    cookiecutter
    pipdeptree
"""

_S = "SCRIPTS"
_r = "requirements"
_l = "local"
_g = "global"


class VenvConfig(object):
    def __init__(self) -> None:
        self.configs = set()  # type: Set[str]
        self._scripts = {}  # type: Dict[str, str]
        self._venvs = {}  # type: Dict[str, VEnv]
        self._scripts_proxy = MappingProxyType(self._scripts)
        self._venvs_proxy = MappingProxyType(self._venvs)

    @staticmethod
    def _file_path(per_user: bool) -> Tuple[str, Path]:
        config_file = (Path('~') if per_user else Path('')) / '.sv_cfg'
        return config_file.as_posix(), Path(path.expanduser(str(config_file))).absolute()

    @staticmethod
    def _requirements(config: ConfigParser, venv: str) -> Set[str]:
        value = config.get(venv, _r, fallback=None) or ''
        return {r for r in value.splitlines() if r}

    def load(self, per_user: bool, in_file: StringIO = None) -> None:
        config_file, config_file_path = self._file_path(per_user)

        if not in_file and not config_file_path.exists():  # pragma: no cover
            return

        self.configs.add(config_file)

        config = ConfigParser(allow_no_value=True)
        with in_file or config_file_path.open() as in_config:
            config.read_file(in_config)

        for v in config:
            if v.islower():
                if per_user:
                    is_local = config.has_option(v, _l)
                else:
                    is_local = not config.has_option(v, _g)
                req = self._requirements(config, v)
                self._venvs.setdefault(v, VEnv(v, local=is_local, requirements=req))

        if config.has_section(_S):
            scripts = config[_S]
            for s in scripts:
                v = scripts[s] or s
                self._scripts[s] = v
                self._venvs.setdefault(v, VEnv(v, local=per_user))

        ignored = [s for s in config.sections() if not (s.islower() or s == _S)]

        if ignored:
            echo("Ignored the following sections of %s: %s" % (config_file, ', '.join(sorted(ignored))))

    def list(self):
        echo("Configs: %s" % sorted(self.configs))
        scripts = {}  # type: Dict[str,Set[str]]
        for s in self.scripts:
            scripts.setdefault(self.scripts[s], set()).add(s)
        for v in self.venvs:
            venv = self.venvs[v]
            echo(str(venv))
            if v in scripts:
                echo("    Scripts: %s" % ', '.join(sorted(scripts[v])))
            if venv.requirements:
                echo("    Requirements: %s" % "\n\t\t".join(venv.requirements))

    @property
    def scripts(self) -> Mapping[str, str]:
        return self._scripts_proxy

    @property
    def venvs(self) -> Mapping[str, VEnv]:
        return self._venvs_proxy

    def register(self, name: str, packages: Iterable[str], per_user: bool, is_local: bool,
                 out_file: StringIO=None, package_scripts=None):
        config_file, config_file_path = self._file_path(per_user)

        config = ConfigParser(allow_no_value=True)
        if config_file_path.exists():
            with config_file_path.open() as in_file:
                config.read_file(in_file)

        if not config.has_section(_S):
            config.add_section(_S)
        requirements = self._requirements(config, name)

        if not package_scripts:  # pragma: no cover
            venv = VEnv(name, local=is_local)
            venv.requirements = requirements
            if venv.create():
                venv.install(*requirements)
            venv.install(*packages)

            try:
                import pkg_resources
            except ImportError:
                echo("Unable to import pkg_resources to register %s into %s" % (sorted(packages), venv))
                return

            pkg_env = pkg_resources.Environment(search_path=[str(venv.abs_path / 'lib' / 'site-packages')])

            def pkg_scripts(p: str) -> Iterable[str]:
                scripts = {}  # type: Dict
                dist = pkg_env[p]
                if len(dist):
                    scripts = dist[0].get_entry_map().get('console_scripts') or {}
                return scripts.keys()

            package_scripts = pkg_scripts

        for p in packages:
            for s in package_scripts(p):
                echo("Registering %s from %s into %s" % (s, p, name))
                config.set(_S, s, name)

        if not config.has_section(name):
            config.add_section(name)
        config.set(name, _r, '\n'.join(sorted(requirements | set(packages))))
        if per_user == is_local:
            config.set(name, _l if per_user else _g, None)

        if out_file:
            config.write(out_file)
        else:
            with config_file_path.open('w') as out_config:
                config.write(out_config)

    def create(self, venv_or_script: str, *extra_params: str, clean: bool=False):
        if venv_or_script in self._venvs:
            venv = self._venvs[venv_or_script]
        elif venv_or_script in self._scripts:
            v = self._scripts[venv_or_script]
            venv = self._venvs[v]
        else:
            echo("Unable to find venv or script %s" % venv_or_script)
            return

        venv.create(clean=clean)
        venv.install(*(tuple(venv.requirements) + extra_params))
