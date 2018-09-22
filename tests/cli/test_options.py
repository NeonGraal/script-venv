#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `script_venv` package cli options."""


from unittest.mock import Mock

from script_venv import cli
from tests.cli.fixtures import CliFixtures
from tests.utils import CliObjectRunner


class TestCliOptions(CliFixtures):
    def test_cli_search_path(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, ['-S', 'Test', 'test'])

        mock_config.set_verbose.assert_not_called()
        mock_config.search_path.assert_called_once_with('Test')
        mock_config.load.assert_called_once_with()

    def test_cli_verbose(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, ['-V', 'test'])

        mock_config.set_verbose.assert_called_once_with()
        mock_config.load.assert_called_once_with()
