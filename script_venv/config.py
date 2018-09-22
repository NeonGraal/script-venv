# -*- coding: utf-8 -*-

""" Config file processing """
from configparser import ConfigParser

from os import getcwd, path
from pathlib2 import Path
from types import MappingProxyType
from typing import Mapping, Set, Dict, Iterable, Tuple, Any, IO, Union  # noqa: F401

from .venv import VEnv, VEnvDependencies, abs_path

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
_l = "location"


class ConfigDependencies(object):  # pragma: no cover
    def echo(self, msg: str):
        raise NotImplementedError()

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
        self._search_path = [path.join('~', '.config'), "$PARENTS", "$CWD"]
        self._scripts = {}  # type: Dict[str, str]
        self._venvs = {}  # type: Dict[str, VEnv]
        self._scripts_proxy = MappingProxyType(self._scripts)
        self._venvs_proxy = MappingProxyType(self._venvs)
        self._verbose = False

    @staticmethod
    def _file_path(raw_path: Union[str, Path]) -> Tuple[str, Path]:
        config_file = Path(raw_path) / '.sv_cfg'
        return config_file.as_posix(), abs_path(config_file)

    @staticmethod
    def _packages_section(config: ConfigParser, venv: str, section: str) -> Set[str]:
        value = config.get(venv, section, fallback='') or ''
        return {r for r in value.splitlines() if r}

    def _config_paths(self):
        for p in self._search_path:
            if p.upper() == '$PARENTS':
                cwd = getcwd()
                drive, full_path = path.splitdrive(cwd)
                parts = full_path.split(path.sep)
                for i in range(2, len(parts)):
                    this_path = path.join(drive + path.sep, *parts[:i])
                    yield path.join(path.relpath(this_path, start=cwd))
            elif p.upper() == '$CWD':
                yield '.'
            else:
                yield p

    def _load_file(self, path: str):
        config_file, config_file_path = self._file_path(Path(path))

        if not self.deps.exists(config_file_path):  # pragma: no cover
            return

        config = ConfigParser(allow_no_value=True)
        with self.deps.read(config_file_path) as in_config:
            config.read_file(in_config)

        for v in config:
            if v.islower():
                new_venv = VEnv(v, self.deps.venv_deps(), path,
                                requirements=self._packages_section(config, v, _r),
                                prerequisites=self._packages_section(config, v, _p),
                                location=config.get(v, _l, fallback='')
                                )
                self._venvs.setdefault(v, new_venv)

        if config.has_section(_s):
            scripts = config[_s]
            for s in scripts:
                v = scripts[s] or s
                self._scripts[s] = v
                new_venv = VEnv(v, self.deps.venv_deps(), path)
                self._venvs.setdefault(v, new_venv)

        ignored = [s for s in config.sections() if not (s.islower() or s == _s)]

        if ignored:
            self.deps.echo("Ignored the following sections of %s: %s" % (config_file, ', '.join(sorted(ignored))))

    def search_path(self, full_path):
        if isinstance(full_path, str):
            self._search_path = full_path.split(path.pathsep)
        elif full_path:
            self._search_path = list(full_path)

    def load(self) -> None:
        for p in self._config_paths():
            self._load_file(p)

    def list(self):
        self.deps.echo("Config Paths: %s" % list(self._config_paths()))
        scripts = {}  # type: Dict[str,Set[str]]
        for s in self.scripts:
            scripts.setdefault(self.scripts[s], set()).add(s)
        for v in self.venvs:
            venv = self.venvs[v]
            self.deps.echo(str(venv))
            if v in scripts:
                self.deps.echo("\tScripts: %s" % ', '.join(sorted(scripts[v])))
            if venv.prerequisites:
                self.deps.echo("\tPrerequisites: %s" % "\n\t\t".join(sorted(venv.prerequisites)))
            if venv.requirements:
                self.deps.echo("\tRequirements: %s" % "\n\t\t".join(sorted(venv.requirements)))

    @property
    def scripts(self) -> Mapping[str, str]:
        return self._scripts_proxy

    @property
    def venvs(self) -> Mapping[str, VEnv]:
        return self._venvs_proxy

    @property
    def verbose(self) -> bool:
        return self._verbose

    def set_verbose(self):
        self._verbose = True

    def info(self, msg):
        if self._verbose:
            self.deps.echo(msg)

    def register(self, name: str, packages: Iterable[str],
                 config_path: str = None, venv_path: str = None) -> None:
        if not config_path:
            config_path = self._search_path[-1]
            self.info("Defaulting config_path to %s" % config_path)
        config_file, config_file_path = self._file_path(config_path)

        config = ConfigParser(allow_no_value=True)
        if self.deps.exists(config_file_path):
            with self.deps.read(config_file_path) as in_file:
                config.read_file(in_file)

        if not config.has_section(_s):
            config.add_section(_s)
        requirements = self._packages_section(config, name, _r)

        venv = VEnv(name, self.deps.venv_deps(), config_path,
                    requirements=requirements,
                    prerequisites=self._packages_section(config, name, _p),
                    location=venv_path)

        for p, s in self.deps.scripts(venv, packages):
            self.deps.echo("Registering %s from %s into %s" % (s, p, name))
            config.set(_s, s, name)

        if not config.has_section(name):
            config.add_section(name)
        config.set(name, _r, '\n'.join(sorted(requirements | set(packages))))

        self.deps.write(config, config_file_path)

    def create(self, venv_or_script: str, *extra_params: str,
               clean: bool = False, update: bool = False) -> None:
        if venv_or_script in self._venvs:
            venv = self._venvs[venv_or_script]
        elif venv_or_script in self._scripts:
            v = self._scripts[venv_or_script]
            venv = self._venvs[v]
        else:
            self.deps.echo("Unable to find venv or script %s" % venv_or_script)
            return

        if not venv.create(clean=clean, update=update):
            self.info("Using venv %s at %s" % (venv.name, venv.env_path))
        install_params = (['-U'] if update else []) + list(sorted(venv.requirements)) + list(extra_params)
        venv.install(*install_params)
