# -*- coding: utf-8 -*-

"""Main module."""
from pathlib import Path

from click import Context, Command, Group

from script_venv.config import VenvConfig
from typing import Iterable, Any


class ScriptVenvCommand(Command):
    def make_context(self, info_name: str, args: Iterable[str], parent: Context=None, **extra: Any) -> Context:
        ctx = Context(self, info_name=info_name, parent=parent, **extra)
        ctx.config = VenvConfig()
        ctx.config.load(Path.cwd())
        ctx.args = args
        return ctx

    def invoke(self, ctx: Context) -> None:
        venv = ctx.config[ctx.info_name.lower()]
        venv.run(ctx.info_name, ctx.args)


class ScriptVenvGroup(Group):
    def get_command(self, ctx: Context, cmd_name: str) -> Command:
        cmd = super(ScriptVenvGroup, self).get_command(ctx, cmd_name)

        if cmd:
            return cmd

        return ScriptVenvCommand(cmd_name)
