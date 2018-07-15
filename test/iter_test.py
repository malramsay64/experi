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

from experi.run import process_command, process_jobs, read_file, variable_matrix

test_cases = sorted(Path("test/data/iter").glob("test*.yml"))


@pytest.mark.xfail(
    sys.version_info < (3, 6), reason="Dictionaries nondeterministic in python < 3.6"
)
@pytest.mark.parametrize("test_file", test_cases)
def test_behaviour(test_file):
    structure = read_file(test_file)
    variables = list(variable_matrix(structure["variables"]))
    print(variables)
    result = []

    jobs_dict = structure.get("jobs")
    if jobs_dict is not None:
        jobs = process_jobs(jobs_dict, variables)
    else:
        input_command = structure.get("command")
        if isinstance(input_command, list):
            command_list = [{"command": cmd} for cmd in input_command]
        else:
            command_list = [{"command": input_command}]

        jobs = process_jobs(command_list, variables)

    for job in jobs:
        result.append([command.cmd for command in job])
    assert result == structure["result"]
