#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Command class."""

from typing import Any, Dict, List, Optional, Tuple, Union


class Command(object):
    """A command to be run for an experiment."""
    _cmd: List[str]
    variables: Dict[str, Any]
    _creates: str = ""
    _requires: str = ""

    def __init__(
        self,
        cmd: Union[List[str], str],
        variables: Dict[str, Any] = None,
        creates: str = "",
        requires: str = "",
    ) -> None:
        self.cmd = cmd
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
    def cmd(self) -> List[str]:
        return [self._format_string(cmd) for cmd in self._cmd]

    @cmd.setter
    def cmd(self, value) -> List[str]:
        if isinstance(value, str):
            self._cmd = [value]
        else:
            self._cmd = list(value)

    def _format_string(self, string: str) -> str:
        return string.format(
            creates=self.creates, requires=self.requires, **self.variables
        )

    def __iter__(self):
        yield from self.cmd

    def __str__(self) -> str:
        return " && ".join(self.cmd)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.cmd == other.cmd
        return False

    def __hash__(self):
        return hash(tuple(self.cmd))


class Job(object):
    """A task to perfrom within a simulation."""
    commands: List[Command]
    shell: str = "bash"
    scheduler_options: Optional[Dict[str, Any]] = None

    def __init__(self, commands, scheduler_options=None) -> None:
        self.commands = commands
        self.scheduler_options = scheduler_options

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
            return_string += '"' + str(command) + '" \\\n'
        return_string += ")"
        return return_string
