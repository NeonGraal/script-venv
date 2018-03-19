# -*- coding: utf-8 -*-

"""Console script for script_venv."""

import click
import sys
from typing import Dict, Set, Iterable  # noqa: F401

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
@click.argument('venv')
@click.argument('package', nargs=-1)
def register_package(venv: str, package: Iterable[str], per_user: bool, is_local: bool, is_global: bool) -> int:
    """Register packages and their scripts in venv"""
    config = VenvConfig()
    config.register(venv, package, per_user, is_local if per_user else not is_global)
    return 0


@main.command(name=":list")
def list_venvs() -> None:
    """List known scripts and venvs"""
    config = VenvConfig()
    config.load(False)
    config.load(True)

    click.echo("Configs: %s" % sorted(config.configs))
    scripts = {}  # type: Dict[str,Set[str]]
    for s in config.scripts:
        scripts.setdefault(config.scripts[s], set()).add(s)
    for v in config.venvs:
        venv = config.venvs[v]
        click.echo(str(venv))
        if v in scripts:
            click.echo("    Scripts: %s" % ', '.join(sorted(scripts[v])))
        if venv.requirements:
            click.echo("    Requirements: %s" % "\n\t\t".join(venv.requirements))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
