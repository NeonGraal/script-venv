===========
Script Venv
===========


.. image:: https://img.shields.io/pypi/v/script-venv.svg
        :target: https://pypi.python.org/pypi/script-venv

.. image:: https://img.shields.io/travis/NeonGraal/script-venv.svg
        :target: https://travis-ci.org/NeonGraal/script-venv

.. image:: https://img.shields.io/appveyor/ci/NeonGraal/script-venv.svg
        :target: https://ci.appveyor.com/project/NeonGraal/script-venv

.. image:: https://readthedocs.org/projects/script-venv/badge/?version=latest
        :target: https://script-venv.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/neongraal/script-venv/shield.svg
     :target: https://pyup.io/repos/github/neongraal/script-venv/
     :alt: Updates



A python package for script (and command) virtualisation with less typing.


* Free software: BSD license
* Documentation: https://script-venv.readthedocs.io.


Features
--------

* Run scripts, either console, gui or pure python, in their own virtual environment.
* Console or gui scripts can be auto registered from their package.
* Virtual environments can be global, user (default) or working directory.

Examples
--------

Presuming ``Example.py`` is registered for the ``example`` use virtual environment::
    $ sv Example.py
    Runs "~/.sv/example/{bin|scripts}/python Example.py"


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
