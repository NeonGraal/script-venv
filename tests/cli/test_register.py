from unittest.mock import Mock

from script_venv import cli
from tests.cli.fixtures import CliFixtures
from tests.utils import CliObjectRunner


class TestCliRegister(CliFixtures):
    def test_cli_register(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_not_called()

    def test_cli_register_venv(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_not_called()

    def test_cli_register_verbose(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, ['-V', ':register', 'test'])

        mock_config.load.assert_called_once_with()
        mock_config.set_verbose.assert_called_once_with()
        mock_config.register.assert_not_called()

    def test_cli_register_package(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package', ), config_path=None, venv_path=None)

    def test_cli_register_packages(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package1', 'package2'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package1', 'package2'), config_path=None, venv_path=None)

    def test_cli_register_config_path(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package', '-P', 'config_path'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package', ), config_path='config_path', venv_path=None)

    def test_cli_register_venv_path(self, mock_config: Mock, run_config: CliObjectRunner):
        run_config.invoke(cli.main, [':register', 'test', 'package', '-V', 'venv_path'])

        mock_config.load.assert_called_once_with()
        mock_config.register.assert_called_once_with('test', ('package', ), config_path=None, venv_path='venv_path')
