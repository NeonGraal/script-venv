# -*- coding: utf-8 -*-

"""Main module."""

from typing import Any, List

from click import Context, Command, Group, echo

from script_venv.factory import ConfigDependenciesImpl
from .config import VenvConfig, ConfigDependencies


class ScriptVenvContext(Context):
    def __init__(self, command: Command, deps: ConfigDependencies, *args: Any, **kwargs: Any) -> None:
        super(ScriptVenvContext, self). __init__(command, *args, **kwargs)
        self.obj = deps
        self.config = VenvConfig(deps=deps)


class ScriptVenvCommand(Command):
    def make_context(self, info_name: str, args: List[str],
                     parent: Context=None, **extra: Any) -> Context:
        deps = (parent.obj if parent else None) or ConfigDependenciesImpl()
        ctx = ScriptVenvContext(self, deps, info_name=info_name, parent=parent, **extra)
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
        if venv.create():
            venv.install(*venv.requirements)

        result = venv.run(cmd, *args)
        ctx.exit(result)


class ScriptVenvGroup(Group):
    def make_context(self, info_name: str, args: List[str],
                     parent: Context=None, deps: ConfigDependencies=None, **extra: Any) -> Context:
        ctx = super(ScriptVenvGroup, self).make_context(info_name, args, parent=parent, **extra)
        ctx.obj = deps or ConfigDependenciesImpl()
        return ctx

    def get_command(self, ctx: Context, cmd_name: str) -> Command:
        cmd = super(ScriptVenvGroup, self).get_command(ctx, cmd_name)

        if cmd:
            return cmd

        return ScriptVenvCommand(cmd_name)
