#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Command class."""

from typing import Any, Dict, List


class Command(object):
    """A command to be run for an experiment."""
    _cmd: str
    variables: Dict[str, Any]
    _creates: str = ""
    _requires: str = ""

    def __init__(
        self,
        cmd: str,
        variables: Dict[str, Any] = None,
        creates: str = "",
        requires: str = "",
    ) -> None:
        self._cmd = cmd
        if variables is not None:
            self.variables = variables
        else:
            self.variables = {}
        self._creates = creates
        self._requires = requires

    @property
    def creates(self) -> str:
        return self._creates.format(**self.variables)

    @property
    def requires(self) -> str:
        return self._requires.format(**self.variables)

    @property
    def cmd(self) -> str:
        return self._cmd.format(
            creates=self.creates, requires=self.requires, **self.variables
        )

    def __str__(self) -> str:
        return self.cmd

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.cmd == other.cmd
        return False

    def __hash__(self):
        return hash(self.cmd)


class Job(object):
    """A task to perfrom within a simulation."""
    commands: List[Command]
    shell: str = "bash"

    def __init__(self, commands) -> None:
        self.commands = commands

    def __iter__(self):
        return iter(self.commands)

    def __len__(self) -> int:
        return len(self.commands)

    def as_bash_array(self) -> str:
        """Return a representation as a bash array.

        This creates a string formatted as a bash arry containing all the commands in the job.

        """
        return_string = "( \\\n"
        for command in self:
            return_string += '"' + command.cmd.strip() + '" \\\n'
        return_string += ")"
        return return_string
