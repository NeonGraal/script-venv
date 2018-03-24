# -*- coding: utf-8 -*-

""" Py.test configuration """

from collections import Callable

import pytest
from click.testing import CliRunner


@pytest.fixture
def click_iso() -> Callable:
    return CliRunner().isolation
