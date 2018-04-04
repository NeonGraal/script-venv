=============
Configuration
=============

Script Venv is configured by one or more ``.sv_cfg`` (Sv config) files.


Sv Config file
==============

A ``.sv_cfg`` file is an ini-like configuration file that may contain a ``SCRIPTS`` section
and / or may contain many ``*venv*`` sections, for example::

    [SCRIPTS]
    Sample.py = sample
    test_script = test

    [test]
    requirements = test_distribution


``[SCRIPTS]`` section
-----------------

The ``SCRIPTS`` section contains a number of mappings between a script and a venv.


``[*venv*]`` section
----------------

A *venv* section contains configuration options for a particular venv.

**Note:** *venv* section names that are not all lowercase will be ignored.


*venv* Configuration options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following configuration option keys are defined:

``requirements``
    A newline separated list of packages that will be installed into this venv when it is created.

``prerequisites``
    A newline separated list of packages that will be installed into this venv before the requirements are installed.
