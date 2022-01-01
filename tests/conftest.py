# -*- coding: utf-8 -*-

""" Generic configuration for the DEER test cases."""

# MIT License (see LICENSE)
# Author: Dániel Hagyárossy <daniel@hagyarossy.hu>, Laszlo Beres <laszloberes@hotmail.hu>

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixture_dir():
    """Return the test fixture directory."""
    this = Path(__file__)
    return this.parent / "fixtures"
