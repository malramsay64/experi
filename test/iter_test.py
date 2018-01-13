#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the behaviour of the looping through variables."""

import pytest
from experirun.run import process

test_cases = [
    {
        'test': {'command': 'echo {var1}',
                 'variables': {'var1': [1, 2, 3, 4, 5]}},
        'result': ['echo 1', 'echo 2', 'echo 3', 'echo 4', 'echo 5']
    },
    {
        'test': {'command': 'echo {var1} {var2}',
                 'variables': {
                     'var1': [1, 2, 3],
                     'var2': [4, 5],
                 }},
        'result': ['echo 1 4', 'echo 1 5', 'echo 2 4', 'echo 2 5', 'echo 3 4', 'echo 3 5']
    },
    {
        'test': {'command': 'echo {var1} {var2}',
                 'variables': {
                     'var1': [{'value': 1}, {'value': 2}, {'value': 3}],
                     'var2': [4, 5],
                 }},
        'result': ['echo 1 4', 'echo 1 5', 'echo 2 4', 'echo 2 5', 'echo 3 4', 'echo 3 5']
    },
    {
        'test': {'command': 'echo {var1} {var2}',
                 'variables': {
                     'var1': [{'value': 1, 'var2': 4},
                              {'value': 2, 'var2': 5},
                              {'value': 3, 'var2': 6}],
                 }},
        'result': ['echo 1 4', 'echo 2 5', 'echo 3 6']
    },
]


@pytest.mark.parametrize('test', test_cases)
def test_behaviour(test):
    assert process(test['test']) == test['result']
