# -*- coding: utf-8 -*-

""" Config file processing """
from configparser import ConfigParser
from click import echo
from os import path
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Set, Dict, Iterable, Tuple, Any, IO  # noqa: F401

from .venv import VEnv, VEnvDependencies

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

_s = "SCRIPTS"
_p = "prerequisites"
_r = "requirements"
_l = "local"
_g = "global"


class ConfigDependencies(object):  # pragma: no cover
    def exists(self, path: Path) -> bool:
        raise NotImplementedError()

    def read(self, path: Path) -> IO[Any]:
        raise NotImplementedError()

    def scripts(self, venv: VEnv, packages: Iterable[str]) -> Iterable[Tuple[str, str]]:
        raise NotImplementedError()

    def write(self, config: ConfigParser, path: Path):
        raise NotImplementedError()

    def venv_deps(self) -> VEnvDependencies:
        raise NotImplementedError()


class VenvConfig(object):
    def __init__(self, deps: ConfigDependencies) -> None:
        self.deps = deps
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
    def _packages_section(config: ConfigParser, venv: str, section: str) -> Set[str]:
        value = config.get(venv, section, fallback=None) or ''
        return {r for r in value.splitlines() if r}

    def load(self, per_user: bool) -> None:
        config_file, config_file_path = self._file_path(per_user)

        if not self.deps.exists(config_file_path):  # pragma: no cover
            return

        self.configs.add(config_file)

        config = ConfigParser(allow_no_value=True)
        with self.deps.read(config_file_path) as in_config:
            config.read_file(in_config)

        for v in config:
            if v.islower():
                if per_user:
                    is_local = config.has_option(v, _l)
                else:
                    is_local = not config.has_option(v, _g)

                new_venv = VEnv(v, self.deps.venv_deps(),
                                local=is_local,
                                requirements=self._packages_section(config, v, _r),
                                prerequisites=self._packages_section(config, v, _p),
                                )
                self._venvs.setdefault(v, new_venv)

        if config.has_section(_s):
            scripts = config[_s]
            for s in scripts:
                v = scripts[s] or s
                self._scripts[s] = v
                new_venv = VEnv(v, self.deps.venv_deps(), local=per_user)
                self._venvs.setdefault(v, new_venv)

        ignored = [s for s in config.sections() if not (s.islower() or s == _s)]

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
                echo("\tScripts: %s" % ', '.join(sorted(scripts[v])))
            if venv.prerequisites:
                echo("\tPrerequisites: %s" % "\n\t\t".join(sorted(venv.prerequisites)))
            if venv.requirements:
                echo("\tRequirements: %s" % "\n\t\t".join(sorted(venv.requirements)))

    @property
    def scripts(self) -> Mapping[str, str]:
        return self._scripts_proxy

    @property
    def venvs(self) -> Mapping[str, VEnv]:
        return self._venvs_proxy

    def register(self, name: str, packages: Iterable[str],
                 per_user: bool, is_local: bool) -> None:
        config_file, config_file_path = self._file_path(per_user)

        config = ConfigParser(allow_no_value=True)
        if self.deps.exists(config_file_path):
            with self.deps.read(config_file_path) as in_file:
                config.read_file(in_file)

        if not config.has_section(_s):
            config.add_section(_s)
        requirements = self._packages_section(config, name, _r)

        venv = VEnv(name, self.deps.venv_deps(),
                    local=is_local,
                    requirements=requirements,
                    prerequisites=self._packages_section(config, name, _p))

        for p, s in self.deps.scripts(venv, packages):
                echo("Registering %s from %s into %s" % (s, p, name))
                config.set(_s, s, name)

        if not config.has_section(name):
            config.add_section(name)
        config.set(name, _r, '\n'.join(sorted(requirements | set(packages))))
        if per_user == is_local:
            config.set(name, _l if per_user else _g, None)

        self.deps.write(config, config_file_path)

    def create(self, venv_or_script: str, *extra_params: str, clean: bool=False) -> None:
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
