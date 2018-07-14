#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for testing `script_venv` package."""
from click import BaseCommand
from click.testing import CliRunner, Result
from configparser import ConfigParser
from io import StringIO
from pathlib2 import Path
from typing import Dict
from unittest.mock import Mock


def config_read(config_deps: Mock, mock_files: Dict[str, str]):
    def exists_callback(file: Path):
        return str(file) in mock_files

    def read_callback(file: Path):
        return StringIO(mock_files[str(file)])

    config_deps.exists.side_effect = exists_callback
    config_deps.read.side_effect = read_callback


def config_write(config_deps: Mock):
    if not isinstance(getattr(config_deps, 'out_str', None), dict):
        config_deps.out_str = {}

    def write_mock(config: ConfigParser, config_path: Path):
        with StringIO() as write_str:
            config.write(write_str)
            config_deps.out_str[str(config_path)] = write_str.getvalue()

    config_deps.write.side_effect = write_mock


def venv_exists(venv_deps: Mock, *mock_dirs: str):
    def exists_callback(exists_dir: Path):
        return str(exists_dir) in mock_dirs

    venv_deps.exists.side_effect = exists_callback


def config_scripts(config_deps: Mock):
    def scripts_callback(_, packages):
        return [(p, '%s.script' % p) for p in packages]

    config_deps.scripts.side_effect = scripts_callback


class StringContaining(str):
    def __eq__(self, other):
        return self in other


class CliObjectRunner(CliRunner):
    def __init__(self, obj: Mock, **kwargs) -> None:
        self.obj = obj
        super(CliObjectRunner, self).__init__(**kwargs)

    def invoke(self, cli: BaseCommand, *args, **extra) -> Result:
        extra['obj'] = self.obj
        return super(CliObjectRunner, self).invoke(cli, *args, **extra)
