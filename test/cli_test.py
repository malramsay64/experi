#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test CLI interaction."""

import pytest
from click.testing import CliRunner

from experi.run import main
from experi.version import __version__


@pytest.fixture
def runner():
    yield CliRunner()


def test_version(runner):
    result = runner.invoke(main, ["--version"])
    assert __version__ in result.output


def test_missing_input_file(runner):
    """Ensure error is raised when input file doesn't exist.

    This should occur both when a file is not specified, and when a file is specified.

    """
    with runner.isolated_filesystem():
        result = runner.invoke(main)
        assert result.exit_code != 0
        result = runner.invoke(main, ["-f", "nonexistant_file.yml"])
        assert result.exit_code != 0
