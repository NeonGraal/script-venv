from unittest.mock import Mock

from script_venv import cli
from tests.cli.fixtures import CliFixtures
from tests.utils import CliObjectRunner


class TestCliList(CliFixtures):
    def test_cli_list(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':list'])

        mock_config.load.assert_called_once_with()
        mock_config.list.assert_called_once_with()

    def test_cli_list_verbose(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, ['-V', ':list'])

        mock_config.load.assert_called_once_with()
        mock_config.set_verbose.assert_called_once_with()
        mock_config.list.assert_called_once_with()
