#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the Command class."""

import pytest

from experi.commands import Command
from experi.run import uniqueify


def test_command_simple():
    cmd = "test"
    command = Command(cmd=cmd)
    assert command.cmd == [cmd]
    assert str(command) == cmd


def test_command_substitution():
    cmd = "test {var1}"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, variables=variables)
    assert command.cmd == [cmd.format(**variables)]
    assert str(command) == cmd.format(**variables)


def test_creates_substitution():
    cmd = "test {var1} {creates}"
    creates = "test.out"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, creates=creates, variables=variables)
    assert command.cmd == [cmd.format(creates=creates, **variables)]
    assert str(command) == cmd.format(creates=creates, **variables)


def test_requires_substitution():
    cmd = "test {var1} {requires}"
    requires = "test.in"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, requires=requires, variables=variables)
    assert command.cmd == [cmd.format(requires=requires, **variables)]
    assert str(command) == cmd.format(requires=requires, **variables)


def test_creates_complex_substitution():
    cmd = "test {creates}"
    creates = "test-{var1}.out"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, creates=creates, variables=variables)
    creates = creates.format(**variables)
    assert command.cmd == [cmd.format(creates=creates, **variables)]
    assert str(command) == cmd.format(creates=creates, **variables)


def test_requires_complex_substitution():
    cmd = "test {requires}"
    requires = "test-{var1}.in"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, requires=requires, variables=variables)
    requires = requires.format(**variables)
    assert command.cmd == [cmd.format(requires=requires, **variables)]
    assert str(command) == cmd.format(requires=requires, **variables)


def test_hashable_command():
    cmd = "test"
    command = Command(cmd=cmd)
    assert hash(command) == hash((cmd,))
    cmd_dict = {command: "Success"}
    assert cmd_dict.get(command) == "Success"


def test_uniqueify_command():
    cmd_list = [Command(cmd="test") for _ in range(5)]
    unique_commands = uniqueify(cmd_list)
    assert len(unique_commands) == 1


def test_command_equality():
    """Test that equality compares classes not just values."""

    class Subcommand(Command):

        def __init__(self, cmd):
            super().__init__(cmd)

    assert Subcommand("test") != Command("test")


def test_cmd_list():
    command = Command(cmd=["test"] * 5)
    assert command.cmd == ["test"] * 5
    assert str(command) == " && ".join(["test"] * 5)


@pytest.mark.parametrize("variables", [("test",), ("test", "test"), ("test1", "test2")])
def test_get_variables(variables):
    format_string = "{" + "}{".join(variables) + "}"
    result = Command(format_string, {i: None for i in variables}).get_variables()
    print(format_string)
    assert sorted(set(variables)) == sorted(result)


def test_get_variables_empty():
    result = Command("test").get_variables()
    assert result == set()


def test_command_init():
    Command("test")
    with pytest.raises(ValueError):
        Command("{test}")
    with pytest.raises(ValueError):
        Command("{test1} {test2}", variables={"test1": ""})
