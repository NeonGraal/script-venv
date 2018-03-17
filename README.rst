===========
Script Venv
===========


.. image:: https://img.shields.io/pypi/v/script-venv.svg
        :target: https://pypi.python.org/pypi/script-venv

.. image:: https://img.shields.io/travis/NeonGraal/script-venv.svg?label=travis&logo=travis
        :target: https://travis-ci.org/NeonGraal/script-venv

.. image:: https://img.shields.io/appveyor/ci/NeonGraal/script-venv.svg?label=appveyor&logo=appveyor
        :target: https://ci.appveyor.com/project/NeonGraal/script-venv

.. image:: https://readthedocs.org/projects/script-venv/badge/?version=latest
        :target: https://script-venv.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/NeonGraal/script-venv/shield.svg
     :target: https://pyup.io/repos/github/NeonGraal/script-venv/
     :alt: Updates



A python package for script (and command) virtualisation with less typing.


* Free software: BSD license
* Documentation: https://script-venv.readthedocs.io.


Features
--------

* Run scripts, either console, gui or pure python, in their own virtual environment (venv).
* Scripts can be registered to a specific venv.
* Console or gui scripts can be auto registered from their package into a venv.
* VEnvs can be per user (default), local (under the current directory) or in a relative directory.
* VEnvs can be registered with requirements, and such venvs can be created as needed.


Examples
--------

If ``Example.py`` is registered for the ``example`` local venv::

    $ sv Example.py
    Runs ".sv/example/bin/python Example.py"

If ``cookiecutter`` is registered for the ``cc`` user venv::

    $ sv cookiecutter
    Runs "~/.sv/cc/bin/cookiecutter"


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
