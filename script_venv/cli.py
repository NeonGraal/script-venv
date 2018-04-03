# -*- coding: utf-8 -*-

"""Console script for script_venv."""
from os import sep, pathsep
from typing import Iterable, cast  # noqa: F401

import click

from script_venv.factory import ConfigDependenciesImpl
from .config import VenvConfig, ConfigDependencies
from .script_venv import ScriptVenvGroup

_IGNORE_UNKNOWN = dict(ignore_unknown_options=True,)


@click.command(name="sv", cls=ScriptVenvGroup, context_settings=_IGNORE_UNKNOWN)
@click.version_option()
@click.option('--config-search-path', '-S', type=click.STRING,
              default=pathsep.join(['~%s.config' % sep, '$PARENTS', '$CWD']),
              help='Path to load .sv_cfg files from')
@click.pass_context
def main(ctx, config_search_path) -> None:
    """Console script for script_venv."""
    deps = cast(ConfigDependencies, ctx.obj) or ConfigDependenciesImpl()
    ctx.obj = VenvConfig(search_path=config_search_path.split(pathsep), deps=deps)
    ctx.obj.load()


@main.command(name=":register")
@click.option('--config-path', '-P', type=click.STRING)
@click.option('--venv-path', '-V', type=click.STRING)
@click.argument('venv', required=True)
@click.argument('package', nargs=-1)
@click.pass_obj
def register_package(obj, venv: str,
                     package: Iterable[str],
                     config_path: str,
                     venv_path: str) -> int:  # pragma: no cover
    """Register packages and their scripts in venv"""
    if not isinstance(obj, VenvConfig):
        raise TypeError("ctx.obj must be a VEnvConfig")
    obj.register(venv, package, config_path=config_path, venv_path=venv_path)
    return 0


@main.command(name=":create", context_settings=_IGNORE_UNKNOWN)
@click.option('--clean', '-C', is_flag=True, help='If the venv exists, clean it before applying requirements')
@click.option('--update', '-U', is_flag=True, help='Update prerequisites, requirements, and pip')
@click.argument('venv_or_script', required=True)
@click.argument('install_params', nargs=-1)
@click.pass_obj
def create_venv(obj, venv_or_script: str,
                install_params: Iterable[str],
                clean: bool, update: bool) -> None:  # pragma: no cover
    """Create or clean venv and apply requirements
    appending any install parameters provided"""
    if not isinstance(obj, VenvConfig):
        raise TypeError("ctx.obj must be a VEnvConfig")
    obj.create(venv_or_script, *install_params, clean=clean, update=update)


@main.command(name=":list")
@click.pass_obj
def list_venvs(obj) -> None:
    """List known scripts and venvs"""
    if not isinstance(obj, VenvConfig):
        raise TypeError("ctx.obj must be a VEnvConfig")
    obj.list()
