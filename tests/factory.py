# -*- coding: utf-8 -*-

""" Doubles for testing"""
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
from typing import IO, Any, Iterable, Tuple

from script_venv.config import ConfigDependencies
from script_venv.venv import VEnv


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

    def write(self, config: ConfigParser, path: Path):
        with StringIO() as out_file:
            config.write(out_file)
            self.out_str = out_file.getvalue()
