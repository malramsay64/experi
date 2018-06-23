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
    assert command.cmd == cmd


def test_command_substitution():
    cmd = "test {var1}"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, variables=variables)
    assert command.cmd == cmd.format(**variables)


def test_creates_substitution():
    cmd = "test {var1} {creates}"
    creates = "test.out"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, creates=creates, variables=variables)
    assert command.cmd == cmd.format(creates=creates, **variables)


def test_requires_substitution():
    cmd = "test {var1} {requires}"
    requires = "test.in"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, requires=requires, variables=variables)
    assert command.cmd == cmd.format(requires=requires, **variables)


def test_creates_complex_substitution():
    cmd = "test {creates}"
    creates = "test-{var1}.out"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, creates=creates, variables=variables)
    creates = creates.format(**variables)
    assert command.cmd == cmd.format(creates=creates, **variables)


def test_requires_complex_substitution():
    cmd = "test {requires}"
    requires = "test-{var1}.in"
    variables = {"var1": "1.0"}
    command = Command(cmd=cmd, requires=requires, variables=variables)
    requires = requires.format(**variables)
    assert command.cmd == cmd.format(requires=requires, **variables)


def test_hashable_command():
    cmd = "test"
    command = Command(cmd=cmd)
    assert hash(command) == hash(cmd)
    cmd_dict = {command: "Success"}
    assert cmd_dict.get(command) == "Success"


def test_uniqueify_command():
    cmd_list = [Command(cmd="test") for _ in range(5)]
    unique_commands = uniqueify(cmd_list)
    assert len(unique_commands) == 1
