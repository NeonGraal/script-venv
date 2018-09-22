from unittest.mock import Mock

from script_venv import cli
from tests.cli.fixtures import CliFixtures
from tests.utils import CliObjectRunner


class TestCliCreate(CliFixtures):
    def test_cli_create(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_not_called()

    def test_cli_create_venv(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=False, update=False)

    def test_cli_create_verbose(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, ['-V', ':create', 'test'])

        mock_config.load.assert_called_once_with()
        mock_config.set_verbose.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=False, update=False)

    def test_cli_create_params(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test', 'param1', 'param2'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', 'param1', 'param2', clean=False, update=False)

    def test_cli_create_clean(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test', '-C'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=True, update=False)

    def test_cli_create_update(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':create', 'test', '-U'])

        mock_config.load.assert_called_once_with()
        mock_config.create.assert_called_once_with('test', clean=False, update=True)
