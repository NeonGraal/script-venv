# -*- coding: utf-8 -*-

"""Console script for script_venv."""

from typing import Iterable  # noqa: F401

import click

from .config import VenvConfig
from .script_venv import ScriptVenvGroup


@click.command(name="sv", cls=ScriptVenvGroup)
@click.version_option()
def main() -> None:
    """Console script for script_venv."""
    pass


@main.command(name=":register")
@click.option('--per-user', '-u', is_flag=True, help='Register in "~/.sv_cfg"')
@click.option('--is-local', '-l', is_flag=True, help='Register as local venv')
@click.option('--is-global', '-g', is_flag=True, help='Register as global venv')
@click.argument('venv', required=True)
@click.argument('package', nargs=-1)
@click.pass_obj
def register_package(obj, venv: str,
                     package: Iterable[str],
                     per_user: bool,
                     is_local: bool,
                     is_global: bool) -> int:  # pragma: no cover
    """Register packages and their scripts in venv"""
    config = VenvConfig(deps=obj)
    config.register(venv, package, per_user, is_local if per_user else not is_global)
    return 0


@main.command(name=":create", context_settings=dict(ignore_unknown_options=True,))
@click.option('--clean', '-c', is_flag=True, help='If the venv exists, clean it before applying requirements')
@click.argument('venv_or_script', required=True)
@click.argument('install_params', nargs=-1)
@click.pass_obj
def create_venv(obj, venv_or_script: str,
                install_params: Iterable[str],
                clean: bool) -> None:  # pragma: no cover
    """Create or clean venv and apply requirements
    appending any install parameters provided"""
    config = VenvConfig(deps=obj)
    config.load(False)
    config.load(True)
    config.create(venv_or_script, *install_params, clean=clean)


@main.command(name=":list")
@click.pass_obj
def list_venvs(obj) -> None:
    """List known scripts and venvs"""
    config = VenvConfig(deps=obj)
    config.load(False)
    config.load(True)
    config.list()
