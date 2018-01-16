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
from typing import (Any, Callable, Dict, Hashable, Iterable, Iterator, List,
                    Union)

from ruamel.yaml import YAML

from .pbs import create_pbs_file

yaml = YAML()


def combine_dictionaries(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return dict(ChainMap(*dicts))


def variable_matrix(variables: Dict[str, Any],
                    parent: str=None,
                    iterator='product') -> Iterator[Dict[str, Any]]:
    _iters: Dict[str, Callable] = {'product': product, 'zip': zip}

    if isinstance(variables, dict):
        key_vars = []
        # Check for iterator variable and remove if nessecary
        # changing the value of the iterator for remaining levels.
        if variables.get('iterator'):
            iterator = variables.get('iterator')
            del variables['iterator']
        for key, value in variables.items():
            # The case where we have a dictionary representing a
            # variable's value, the value is stored in 'value'.
            if key == 'value':
                key = parent
            key_vars.append(list(variable_matrix(value, key, iterator)))
        # Iterate through all possible products generating a dictionary
        for i in _iters[iterator](*key_vars):
            yield combine_dictionaries(i)

    elif isinstance(variables, list):
        for item in variables:
            yield from variable_matrix(item, parent, iterator)

    # Stopping condition -> we have either a single value from a list
    # or a value had only one item
    else:
        yield {parent: variables}


# TODO update type inference for this when issues in mypy are closed
def uniqueify(my_list: Any) -> List[Any]:
    return list(dict.fromkeys(my_list))


def process_command(commands: Union[str, List[str]],
                    matrix: List[Dict[str, Any]]) -> Iterator[List[str]]:
    # Ensure commands is a list
    if isinstance(commands, str):
        commands = [commands]

    for command in commands:
        # substitute variables into command
        c_list = [command.format(**kwargs) for kwargs in matrix]
        yield uniqueify(c_list)


def read_file(filename: str='experiment.yml') -> Dict['str', Any]:
    with open(filename, 'r') as stream:
        structure = yaml.load(stream)
    return structure

def process_file(filename: str='experiment.yml') -> List[str]:
    # Read input file
    structure = read_file(filename)

    # create variable matrix
    variables = list(variable_matrix(structure.get('variables')))
    assert variables

    command_groups = process_command(structure.get('command'), variables)

    # Check for pbs options
    if structure.get('pbs'):
        if structure.get('name'):
            structure['pbs'].setdefault('name', structure.get('name'))
        return [create_pbs_file(command_group, structure.get('pbs'))
                for command_group in command_groups]

    return command_groups


def main() -> None:
    # Process and run commands
    for command_group in process_file():
        for command in command_group:
            subprocess.run(command.split())
