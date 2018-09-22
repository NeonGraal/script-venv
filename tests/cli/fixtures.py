#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test fixtures for `script_venv` package cli tests."""


from os import getcwd, chdir, path
from typing import Iterable
from unittest.mock import Mock, MagicMock, PropertyMock

import pytest

from script_venv.config import VenvConfig
from tests.utils import CliObjectRunner


class CliFixtures(object):
    @pytest.fixture
    def mock_config(self) -> Mock:
        mock = MagicMock(spec=VenvConfig)
        type(mock).verbose = PropertyMock(spec=bool)
        return mock

    @pytest.fixture
    def run_config(self, mock_config: Mock) -> Iterable[CliObjectRunner]:
        old_cwd = getcwd()
        try:
            chdir(path.dirname(__file__))
            yield CliObjectRunner(mock_config)
        finally:
            chdir(old_cwd)
