# -*- coding: utf-8 -*-

"""Console script for script_venv."""
import sys
import click

from .script_venv import ScriptVenvGroup


@click.command(name="sv", cls=ScriptVenvGroup)
@click.version_option()
def main():
    # type: () -> None
    """Console script for script_venv."""
    pass


@main.command(name=":update")
@click.argument('venv', type=click.STRING)
def update(venv):
    # type: (str) -> int
    """Update venv"""
    click.echo("update venv: " + venv)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
