#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'typing ; python_version < "3.5"', 'pathlib2', ]

setup_requirements = ['pytest-runner', 'setuptools_scm', ]

test_requirements = ['pytest', 'pytest-cov', 'pytest-flake8', 'pytest-mypy', 'mypy', ]

setup(
    author="Struan Lyall Judd",
    author_email='sv@scifi.geek.nz',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="A python package for script (and command) virtualisation with less typing.",
    entry_points={
        'console_scripts': [
            'sv=script_venv.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='script_venv',
    name='script_venv',
    packages=find_packages(include=['script_venv']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/neongraal/script_venv',
    use_scm_version=True,
    zip_safe=False,
)
