#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Utility fixtures for use within pytest."""

from tempfile import TemporaryDirectory
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def tmp_dir():
    with TemporaryDirectory() as dst:
        yield Path(dst)
