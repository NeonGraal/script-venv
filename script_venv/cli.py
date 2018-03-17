# -*- coding: utf-8 -*-

"""Console script for script_venv."""
import sys
import click
from pathlib import Path

from script_venv.config import VenvConfig
from .script_venv import ScriptVenvGroup


@click.command(name="sv", cls=ScriptVenvGroup)
@click.version_option()
def main() -> None:
    """Console script for script_venv."""
    pass


@main.command(name=":update")
@click.argument('venv', type=click.STRING)
def update(venv: str) -> int:
    """Update venv"""
    click.echo("update venv: " + venv)
    return 0


@main.command(name=":list")
def list() -> None:
    """List known venvs"""
    config = VenvConfig()
    config.load(Path.cwd())

    for s in config.scripts():
        print(s, '->', config[s].name)
    for v in config.venvs():
        print(v)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
