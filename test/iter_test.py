#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the behaviour of the looping through variables.

This is a series of tests that are defining the interface of the module,
primarily the iteration of the variables."""

import sys
from pathlib import Path

import pytest

from experi.run import process_command, read_file, variable_matrix

test_cases = Path("test/data/iter").glob("test*.yml")


@pytest.mark.xfail(
    sys.version_info < (3, 6), reason="Dictionaries nondeterministic in python < 3.6"
)
@pytest.mark.parametrize("test_file", test_cases)
def test_behaviour(test_file):
    test = read_file(test_file)
    variables = list(variable_matrix(test["variables"]))
    print(variables)
    print(test["command"])
    result = []
    for command_group in process_command(test["command"], variables):
        result.append([command.cmd for command in command_group])
    assert result == test["result"]
