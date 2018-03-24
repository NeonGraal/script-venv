# -*- coding: utf-8 -*-

""" Doubles for testing"""
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
from typing import IO, Any, Iterable, Tuple, Dict

from script_venv.config import ConfigDependencies
from script_venv.venv import VEnv, VEnvDependencies


class TestVEnvDependencies(VEnvDependencies):
    path_exists = False
    created = ("", False)
    run = ([], {})  # type: Tuple[Iterable[str], Dict[str, str]]
    ret_code = -1

    def exists(self, path: Path) -> bool:
        return self.path_exists

    def runner(self, cmd: Iterable[str], env: Dict[str, str] = None) -> int:
        self.run = (cmd, env)
        return self.ret_code

    def creator(self, path: Path, clear: bool = False) -> None:
        self.created = (str(path), clear)


class TestConfigDependencies(ConfigDependencies):
    in_str = ""
    out_str = ""

    def exists(self, path: Path) -> bool:
        return bool(self.in_str)

    def read(self, path: Path) -> IO[Any]:
        # noinspection PyTypeChecker
        return StringIO(self.in_str)

    def scripts(self, venv: VEnv, packages: Iterable[str]) -> Iterable[Tuple[str, str]]:
        return [(p, p + ".script") for p in packages]

    def venv_deps(self) -> VEnvDependencies:
        return TestVEnvDependencies()

    def write(self, config: ConfigParser, path: Path):
        with StringIO() as out_file:
            config.write(out_file)
            self.out_str = out_file.getvalue()
