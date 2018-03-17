# -*- coding: utf-8 -*-

"""Main module."""

from click import Context, Command, Group, echo
from pathlib import Path
from typing import Iterable, Any

from .config import VenvConfig


class ScriptVenvContext(Context):
    def __init__(self, *args, **kwargs):
        super(ScriptVenvContext, self). __init__(*args, **kwargs)
        self.config = VenvConfig()


class ScriptVenvCommand(Command):
    def make_context(self, info_name: str, args: Iterable[str], parent: Context=None, **extra: Any) -> Context:
        ctx = ScriptVenvContext(self, info_name=info_name, parent=parent, **extra)
        ctx.config.load(Path('~'), False)
        ctx.config.load(Path(''), True)
        ctx.args = list(args)
        return ctx

    def invoke(self, ctx: Context) -> None:
        name = ctx.info_name.lower()
        cmd = ctx.info_name
        args = ctx.args
        if isinstance(ctx, ScriptVenvContext):
            if name in ctx.config.scripts:
                v = ctx.config.scripts[name]
            elif name in ctx.config.venvs:
                v = name
                if len(args) > 0:
                    cmd = args.pop(0)
                else:
                    echo('Insufficient parameters', err=True)
                    return
            else:
                echo('Unknown script or venv: "%s"' % ctx.info_name, err=True)
                return
            venv = ctx.config.venvs[v]
            venv.run(cmd, args)


class ScriptVenvGroup(Group):
    def get_command(self, ctx: Context, cmd_name: str) -> Command:
        cmd = super(ScriptVenvGroup, self).get_command(ctx, cmd_name)

        if cmd:
            return cmd

        return ScriptVenvCommand(cmd_name)
