# -*- coding: utf-8 -*-

"""Main module."""

from typing import Any, List

from click import Context, Command, Group, echo

from script_venv.factory import ConfigDependenciesImpl
from .config import VenvConfig, ConfigDependencies


class ScriptVenvCommand(Command):
    def invoke(self, ctx: Context) -> None:
        if not isinstance(ctx.obj, VenvConfig):  # pragma: no cover
            raise TypeError("ctx.obj must be a VEnvConfig")

        cmd = ctx.info_name
        if not cmd:  # pragma: no cover
            raise TypeError("ctx.info_name must be given")

        name = cmd.lower()
        args = ctx.args

        if name in ctx.obj.scripts:
            v = ctx.obj.scripts[name]
        elif name in ctx.obj.venvs:
            v = name
            if len(args) == 0:  # pragma: no cover
                echo('Insufficient parameters', err=True)
                return
            cmd = args.pop(0)
        else:  # pragma: no cover
            echo('Unknown script or venv: "%s"' % ctx.info_name, err=True)
            return

        venv = ctx.obj.venvs[v]
        if venv.create():
            venv.install(*venv.requirements)
        else:
            ctx.obj.info("Using venv %s at %s" % (venv.name, venv.env_path))

        result = venv.run(cmd, *args)
        ctx.exit(result)


class ScriptVenvGroup(Group):
    def make_context(self, info_name: str, args: List[str],
                     parent: Context=None, deps: ConfigDependencies=None, **extra: Any) -> Context:
        ctx = super(ScriptVenvGroup, self).make_context(info_name, args, parent=parent, **extra)
        ctx.obj = ctx.obj or deps or ConfigDependenciesImpl()
        return ctx

    def get_command(self, ctx: Context, cmd_name: str) -> Command:
        cmd = super(ScriptVenvGroup, self).get_command(ctx, cmd_name)

        if not cmd:
            cmd = ScriptVenvCommand(cmd_name)
            cmd.allow_extra_args = True
            cmd.ignore_unknown_options = True

        return cmd
