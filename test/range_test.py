#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the loading of a range object."""

from textwrap import dedent

import numpy as np
import pytest
import yaml

from experi.run import variable_matrix


def get_ranges():
    return [
        (
            """
            arange:
                stop: 10
            """,
            list(np.arange(10)),
        ),
        (
            """
            arange:
                start: 1
                stop: 10
            """,
            list(np.arange(1, 10)),
        ),
        (
            """
            arange:
                start: 1.
                stop: 10
            """,
            list(np.arange(1., 10)),
        ),
        (
            """
            arange: 10
            """,
            list(np.arange(10)),
        ),
    ]


def parse_string(string):
    result = yaml.safe_load(dedent(string))
    return list(variable_matrix(result, parent="test"))


def generate_comparison(values):
    return [{"test": value} for value in values]


@pytest.mark.parametrize("string, expected", get_ranges())
def test_range(string, expected):
    result = parse_string(string)
    expected = generate_comparison(expected)
    assert result == expected


def test_stop_required():
    with pytest.raises(ValueError):
        parse_string("arange: {start: 10}")


def test_range_errors():
    with pytest.raises(ValueError):
        parse_string("arange: [1, 2, 3]")


def create_string(start, stop, step, dtype):
    return f"arange: {{start: {start}, stop: {stop}, step: {step}, dtype: {dtype}}}"


# No none in start to remove conditional in test
@pytest.mark.parametrize("start", [1, 10, 10.])
@pytest.mark.parametrize("stop", [2, 20, 20.])
@pytest.mark.parametrize("step", [1, 10, 10.])
@pytest.mark.parametrize("dtype", ["float", "int"])
def test_values(start, stop, step, dtype):
    result = parse_string(create_string(start, stop, step, dtype))
    expected = generate_comparison(np.arange(start, stop, step, dtype))
    assert result == expected
