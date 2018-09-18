# -*- coding: utf-8 -*-

"""Console script for script_venv."""
from typing import Iterable, cast  # noqa: F401

import click

from script_venv.factory import ConfigDependenciesImpl
from .config import VenvConfig, ConfigDependencies
from .script_venv import ScriptVenvGroup

_IGNORE_UNKNOWN = dict(ignore_unknown_options=True, )


@click.command(name="sv", cls=ScriptVenvGroup, context_settings=_IGNORE_UNKNOWN)
@click.version_option()
@click.option('--config-search-path', '-S', type=click.STRING,
              help='Path to load .sv_cfg files from')
@click.option('--verbose', '-V', is_flag=True, help="Show messages")
@click.pass_context
def main(ctx, config_search_path: str, verbose: bool) -> None:
    """Console script for script_venv."""
    if not isinstance(ctx.obj, VenvConfig):
        deps = cast(ConfigDependencies, ctx.obj) or ConfigDependenciesImpl()
        ctx.obj = VenvConfig(deps=deps)
    if verbose:
        ctx.obj.set_verbose()
    if config_search_path:
        ctx.obj.search_path(config_search_path)
    ctx.obj.load()


@main.command(name=":list")  # type: ignore
@click.pass_obj
def list_venvs(obj) -> None:
    """List known scripts and venvs"""
    if not isinstance(obj, VenvConfig):  # pragma: no cover
        raise TypeError("ctx.obj must be a VEnvConfig")
    obj.list()


@main.command(name=":create", context_settings=_IGNORE_UNKNOWN)  # type: ignore
@click.option('--clean', '-C', is_flag=True, help='If the venv exists, clean it before applying requirements')
@click.option('--update', '-U', is_flag=True, help='Update prerequisites, requirements, and pip')
@click.argument('venv_or_script', required=True)
@click.argument('install_params', nargs=-1)
@click.pass_obj
def create_venv(obj, venv_or_script: str,
                install_params: Iterable[str],
                clean: bool, update: bool) -> None:
    """Create or clean venv and apply requirements
    appending any install parameters provided"""
    if not isinstance(obj, VenvConfig):  # pragma: no cover
        raise TypeError("ctx.obj must be a VEnvConfig")
    obj.create(venv_or_script, *install_params, clean=clean, update=update)


@main.command(name=":register", context_settings=_IGNORE_UNKNOWN)  # type: ignore
@click.option('--config-path', '-P', type=click.STRING)
@click.option('--venv-path', '-V', type=click.STRING)
@click.argument('venv', required=True)
@click.argument('package', nargs=-1, required=True)
@click.pass_obj
def register_package(obj, venv: str,
                     package: Iterable[str],
                     config_path: str,
                     venv_path: str) -> int:
    """Register packages and their scripts in venv"""
    if not isinstance(obj, VenvConfig):  # pragma: no cover
        raise TypeError("ctx.obj must be a VEnvConfig")
    obj.register(venv, package, config_path=config_path, venv_path=venv_path)
    return 0
