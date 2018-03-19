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
            --user      register the venv, and the package's scripts, in "~/.sv_cfg" (Default is ".sv_cfg"
            --local     register the venv as local (Default if not --user)
            --global    register the venv as global (Default if --user)
