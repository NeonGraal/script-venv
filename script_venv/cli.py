# -*- coding: utf-8 -*-

"""Console script for script_venv."""
import click
from pathlib import Path
import sys

from .config import VenvConfig
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
    """List known scripts and venvs"""
    config = VenvConfig()
    config.load(Path('~'), False)
    config.load(Path(''), True)

    print("Configs:", sorted(config.cfgs))
    for s in config.scripts:
        print(s, '->', config.scripts[s])
    for v in config.venvs:
        print(config.venvs[v])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
