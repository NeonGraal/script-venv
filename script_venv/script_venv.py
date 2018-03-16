# -*- coding: utf-8 -*-

"""Main module."""
import click
from click.core import Context
from typing import Any
from typing import List
from click.core import Command
from typing import Union


class ScriptVenvCommand(click.Command):
    def make_context(self, info_name, args, parent=None, **extra):
        # type: (str, List[str], Context, **Any) -> Context
        ctx = click.Context(self, info_name=info_name, parent=parent, **extra)
        ctx.args = args
        return ctx

    def invoke(self, ctx):
        # type: (Context) -> None
        click.echo(f"{self.name} args: {ctx.args}")


class ScriptVenvGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        # type: (Context, str) -> Union[Command, ScriptVenvCommand]
        cmd = super(ScriptVenvGroup, self).get_command(ctx, cmd_name)

        if cmd:
            return cmd

        return ScriptVenvCommand(cmd_name)
