from configparser import ConfigParser
from io import StringIO
from pathlib import Path
from unittest.mock import Mock


def config_read(deps: Mock, in_str: str):
    deps.exists.return_value = True
    deps.read.return_value = StringIO(in_str)


def config_write(deps: Mock):
    def write_mock(config: ConfigParser, _config_path: Path):
        with StringIO() as write_str:
            config.write(write_str)
            deps.out_str = write_str.getvalue()

    deps.write.side_effect = write_mock
