#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Ensure the example files are valid."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from experi.run import main


@pytest.fixture
def runner():
    yield CliRunner()


def example_files():
    for f in Path("examples").glob("*.yml"):
        yield str(f)


@pytest.mark.parametrize("filename", example_files())
def test_examples(runner, filename):
    assert Path(filename).is_file()
    result = runner.invoke(main, ["--dry-run", "--input-file", filename])
    assert result.exit_code == 0, result.output
