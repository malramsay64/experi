#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.


from hypothesis import given, settings
from hypothesis.strategies import characters, text

from experi.run import process_command, variable_matrix


@given(
    text(alphabet=characters(whitelist_categories=("L")), min_size=1),
    text(alphabet=characters(blacklist_characters=(":", "{", "}", "[", "]", "!", "."))),
)
@settings(max_examples=1000)
def test_variable_generality(variable_start, variable_end):
    variable_name = variable_start + variable_end
    var_dict = {variable_name: [1, 2, 3, 4, 5]}
    variables = variable_matrix(var_dict)
    cmd_list = [
        str(cmd) for cmd in process_command("echo {" + variable_name + "}", variables)
    ]
    assert cmd_list == ["echo 1", "echo 2", "echo 3", "echo 4", "echo 5"]
