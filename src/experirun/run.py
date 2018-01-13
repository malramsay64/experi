#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Run an experiment varying a number of variables."""

import subprocess
from collections import ChainMap
from itertools import product
from typing import Any, Dict, List, Union, Iterator

import yaml


def combine_dictionaries(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return dict(ChainMap(*dicts))


def variable_matrix(variables: Dict[str, Any], parent: str=None) -> Iterator[Dict[str, Any]]:
    if isinstance(variables, dict):
        key_vars = []
        for key, value in variables.items():
            # The case where we have a dictionary representing a
            # variable's value, the value is stored in 'value'.
            if key == 'value':
                key = parent
            key_vars.append(list(variable_matrix(value, key)))
        # Iterate through all possible products generating a dictionary
        for i in product(*key_vars):
            yield combine_dictionaries(i)

    elif isinstance(variables, list):
        for item in variables:
            yield from variable_matrix(item, parent)

    # Stopping condition -> we have either a single value from a list
    # or a value had only one item
    else:
        yield {parent: variables}


def process_command(commands: Union[str, List[str]], matrix: List[Dict[str, Any]]) -> Iterator[List[str]]:
    # Ensure commands is a list
    if isinstance(commands, str):
        commands = [commands]

    for command in commands:
        # substitute variables into command
        yield [command.format(**kwargs) for kwargs in matrix]


def read_file(filename: str='experiment.yml') -> Dict['str', Any]:
    with open(filename, 'r') as stream:
        structure = yaml.load(stream)
    return structure


def main() -> None:
    # Read input file
    structure = read_file()

    # create variable matrix
    variables = list(variable_matrix(structure.get('variables')))
    assert len(variables) > 0

    # Process and run commands
    for command_group in process_command(structure.get('command'), variables):
        for command in command_group:
            subprocess.run(command.split())

