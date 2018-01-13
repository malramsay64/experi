#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Run an experiment varying a number of variables."""

from itertools import product
from string import Formatter
from typing import Any, Dict, List
from collections import ChainMap
from subprocess import call
from os import PathLike

import yaml


def collect_format_vars(string: str) -> List[str]:
    """Extract the variables from a format string to a list."""
    # Parse retuns a tuple of 4 values being (literal_text, field_name, format_spec, conversion)
    # This function is only concerned with the field_name so the rest is ignored.
    return [field_name for _, field_name, *_ in Formatter().parse(string) if field_name is not None]


def combine_dictionaries(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return dict(ChainMap(*dicts))


def variable_matrix(variables: Dict[str, Any], parent: str=None) -> Dict[str, Any]:
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


def process_command(structure: Dict[str, Any]) -> List[str]:
    # Create variable matrix
    matrix = variable_matrix(structure.get('variables'))

    # Check variables in command exist
    command_vars = collect_format_vars(structure.get('command'))

    # substitute variables into command
    return [structure.get('command').format(**kwargs) for kwargs in matrix]


def read_file(filename: PathLike='experiment.yml') -> Dict['str', Any]:
    with open(filename, 'r') as stream:
        structure = yaml.load(stream)
    return structure


def main() -> None:
    # Read input file
    structure = read_file()

    # Process commands
    commands = process_command(structure)

    # Run commands
    for command in commands:
        call(command.split())
