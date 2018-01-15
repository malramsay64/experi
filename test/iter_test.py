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

import pytest
from experirun.run import process_command, variable_matrix

test_cases = [
    # Test the most basic behaviour, iterating through a list
    (
        {'command': 'echo {var1}',
         'variables': {'var1': [1, 2, 3, 4, 5]}},
        [['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5']]
     ),
    # Test iterating over the product of two variables
    (
        {'command': 'echo {var1} {var2}',
         'variables': {
             'var1': [1, 2, 3],
             'var2': [4, 5],
         }},
     [['echo 1 4', 'echo 1 5', 'echo 2 4', 'echo 2 5', 'echo 3 4', 'echo 3 5']]
     ),
    # Test setting 'value' in a dictionary, allowing nested variables
    (
        {'command': 'echo {var1} {var2}',
         'variables': {
             'var1': [{'value': 1}, {'value': 2}, {'value': 3}],
             'var2': [4, 5],
         }},
     [['echo 1 4', 'echo 1 5', 'echo 2 4', 'echo 2 5', 'echo 3 4', 'echo 3 5']]
     ),
    # test nested dictionaries of variables
    (
        {'command': 'echo {var1} {var2}',
         'variables': {
             'var1': [{'value': 1, 'var2': 4},
                      {'value': 2, 'var2': 5},
                      {'value': 3, 'var2': 6}],
         }},
        [['echo 1 4', 'echo 2 5', 'echo 3 6']]
     ),
    # Test multiple commands
    (
        {'command': ['echo {var1}', 'echo {var1}'],
         'variables': {'var1': [1, 2, 3, 4, 5]}},
        [['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5'],
        ['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5']]
     ),
    # Test multiple commands with different vars with the zip iterator
    (
        {'command': ['echo {var1}', 'echo {var2}'],
         'variables': {'var1': [1, 2, 3, 4, 5],
                       'var2': [11, 12, 13, 14, 15],
                       'iterator': 'zip',
                       }},
        [['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5'],
        ['echo 11', 'echo 12', 'echo 13', 'echo 14', 'echo 15']]
     ),
    # Test nested zip iterator
    (
        {'command': ['echo {var1} {var2} {var3}'],
         'variables': {'var1': {'value': [1, 2, 3],
                                'var3': [1, 2],
                                'iterator': 'product'},
                       'var2': [11, 12, 13, 14, 15, 16],
                       'iterator': 'zip',
                       }},
        [['echo 1 11 1', 'echo 1 12 2', 'echo 2 13 1',
          'echo 2 14 2', 'echo 3 15 1', 'echo 3 16 2']],
     ),
    # Test unique commands
    (
        {'command': 'echo {var1}',
         'variables': {
             'var1': [1, 2, 3],
             'var2': [4, 5],
         }},
     [['echo 1', 'echo 2', 'echo 3']]
     ),
    # Test string variables
    (
        {'command': 'echo {var1}',
         'variables': {
             'var1': ['test', 'string', 'types'],
         }},
     [['echo test', 'echo string', 'echo types']]
     ),
]


@pytest.mark.parametrize('test, result', test_cases)
def test_behaviour(test, result):
    variables = list(variable_matrix(test['variables']))
    print(variables)
    print(test['command'])
    assert list(process_command(test['command'], variables)) == result
