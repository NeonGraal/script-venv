# -*- coding: utf-8 -*-

"""Console script for script_venv."""

import click
from pathlib import Path
import sys
from typing import Dict, Set  # noqa: F401

from .config import VenvConfig
from .script_venv import ScriptVenvGroup


@click.command(name="sv", cls=ScriptVenvGroup)
@click.version_option()
def main() -> None:
    """Console script for script_venv."""
    pass


@main.command(name=":update")
@click.argument('venv', type=click.STRING)
def update_venvs(venv: str) -> int:
    """Update venv"""
    click.echo("update venv: " + venv)
    return 0


@main.command(name=":list")
def list_venvs() -> None:
    """List known scripts and venvs"""
    config = VenvConfig()
    config.load(Path('~'), False)
    config.load(Path(''), True)

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
