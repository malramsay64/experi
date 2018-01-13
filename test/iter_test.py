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
    (
        {'command': 'echo {var1}',
         'variables': {'var1': [1, 2, 3, 4, 5]}},
        [['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5']]
     ),
    (
        {'command': 'echo {var1} {var2}',
         'variables': {
             'var1': [1, 2, 3],
             'var2': [4, 5],
         }},
     [['echo 1 4', 'echo 1 5', 'echo 2 4', 'echo 2 5', 'echo 3 4', 'echo 3 5']]
     ),
    (
        {'command': 'echo {var1} {var2}',
         'variables': {
             'var1': [{'value': 1}, {'value': 2}, {'value': 3}],
             'var2': [4, 5],
         }},
     [['echo 1 4', 'echo 1 5', 'echo 2 4', 'echo 2 5', 'echo 3 4', 'echo 3 5']]
     ),
    (
        {'command': 'echo {var1} {var2}',
         'variables': {
             'var1': [{'value': 1, 'var2': 4},
                      {'value': 2, 'var2': 5},
                      {'value': 3, 'var2': 6}],
         }},
        [['echo 1 4', 'echo 2 5', 'echo 3 6']]
     ),
    (
        {'command': ['echo {var1}', 'echo {var1}'],
         'variables': {'var1': [1, 2, 3, 4, 5]}},
        [['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5'],
        ['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5']]
     ),
]


@pytest.mark.parametrize('test, result', test_cases)
def test_behaviour(test, result):
    variables = list(variable_matrix(test['variables']))
    print(variables)
    print(test['command'])
    assert list(process_command(test['command'], variables)) == result
