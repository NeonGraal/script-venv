=====
Usage
=====

To use Script Venv::

    sv [SV-OPTS] SCRIPT [ARGUMENTS ...]
    sv [SV-OPTS] COMMAND [ARGUMENTS ...]

or::

    sv [SV-OPTS] VENV COMMAND-LINE ...


List
====

To list registered Venvs and their scripts::

    sv :list


Register
========

To register a package and it's scripts to a venv::

    sv :register [OPTS] VENV PACKAGE ...

        register options:
            --user, -u      register the venv, and the package's scripts, in "~/.sv_cfg" (Default is ".sv_cfg"
            --local, -l     register the venv as local (Default if not --user)
            --global, -g    register the venv as global (Default if --user)


Create
======

To create, clean or update the packages in a venv::

    sv :create [OPTS] VENV_OR_SCRIPT [EXTRA_ARGS ...]

        create options:
            --clean, -C     Clean the venv if it already exists
            --update, -U    Update any prerequisites, requirements and even pip if needed
