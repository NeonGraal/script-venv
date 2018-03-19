# -*- coding: utf-8 -*-

"""Main module."""

from click import Context, Command, Group, echo
from typing import Iterable, Any

from .config import VenvConfig


class ScriptVenvContext(Context):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ScriptVenvContext, self). __init__(*args, **kwargs)
        self.config = VenvConfig()


class ScriptVenvCommand(Command):
    def make_context(self, info_name: str, args: Iterable[str], parent: Context=None, **extra: Any) -> Context:
        ctx = ScriptVenvContext(self, info_name=info_name, parent=parent, **extra)
        ctx.config.load(False)
        ctx.config.load(True)
        ctx.args = list(args)
        return ctx

    def invoke(self, ctx: Context) -> None:
        if not isinstance(ctx, ScriptVenvContext):  # pragma: no cover
            return

        name = ctx.info_name.lower()
        cmd = ctx.info_name
        args = ctx.args

        if name in ctx.config.scripts:
            v = ctx.config.scripts[name]
        elif name in ctx.config.venvs:
            v = name
            if len(args) == 0:  # pragma: no cover
                echo('Insufficient parameters', err=True)
                return
            cmd = args.pop(0)
        else:  # pragma: no cover
            echo('Unknown script or venv: "%s"' % ctx.info_name, err=True)
            return

        venv = ctx.config.venvs[v]
        if not venv.exists():
            if not venv.requirements:
                echo('Cannot create venv "%s" as no requirements' % v)
                return

            if not venv.create():  # pragma: no cover
                echo('Creation of venv "%s" failed' % v)
                return

            result = venv.run('pip', ['install'] + list(venv.requirements))

        result = venv.run(cmd, args)
        ctx.exit(result)


class ScriptVenvGroup(Group):
    def get_command(self, ctx: Context, cmd_name: str) -> Command:
        cmd = super(ScriptVenvGroup, self).get_command(ctx, cmd_name)

        if cmd:
            return cmd

        return ScriptVenvCommand(cmd_name)
