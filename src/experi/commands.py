#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Command class."""

import logging
from pathlib import Path
from string import Formatter
from typing import Any, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command:
    """A command to be run for an experiment."""

    _cmd: List[str]
    variables: Dict[str, Any]
    _creates: str = ""
    _requires: str = ""
    __formatter = Formatter()

    def __init__(
        self,
        cmd: Union[List[str], str],
        variables: Dict[str, Any] = None,
        creates: str = "",
        requires: str = "",
    ) -> None:
        if isinstance(cmd, str):
            self.cmd = [cmd]
        else:
            self.cmd = cmd

        if variables is not None:
            self.variables = variables
        else:
            self.variables = {}

        # variables in cmd are a subset of those passed in
        if self.get_variables() > set(self.variables.keys()):
            logger.debug("Command Keys: %s", self.get_variables())
            logger.debug("Variables Keys: %s", set(self.variables.keys()))
            # Find missing variables
            missing_vars = self.get_variables() - set(self.variables.keys())
            raise ValueError(f"The following variables have no value: {missing_vars}")

        self._creates = creates
        self._requires = requires

    def get_variables(self) -> Set[str]:
        """Find all the variables specified in a format string.

        This returns a list of all the different variables specified in a format string,
        that is the variables inside the braces.

        """
        variables = set()
        for cmd in self._cmd:
            for var in self.__formatter.parse(cmd):
                logger.debug("Checking variable: %s", var)
                # creates and requires are special class values
                if var[1] is not None and var[1] not in ["creates", "requires"]:
                    variables.add(var[1])
        return variables

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
    def cmd(self, value) -> None:
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
        return " && ".join(self.cmd).strip()

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.cmd == other.cmd
        return False

    def __hash__(self):
        return hash(tuple(self.cmd))


class Job:
    """A task to perform within a simulation."""

    commands: List[Command]
    shell: str = "bash"
    scheduler_options: Optional[Dict[str, Any]] = None
    use_dependencies: bool = False
    directory: Optional[Path] = None

    def __init__(
        self, commands, scheduler_options=None, directory=None, use_dependencies=False
    ) -> None:
        if use_dependencies and directory is None:
            raise ValueError("Directory must be set when overwrite is False.")

        self.commands = commands
        self.scheduler_options = scheduler_options
        self.directory = directory
        self.use_dependencies = use_dependencies

    def __iter__(self):
        if self.use_dependencies and self.directory is None:
            raise ValueError("Directory must be set when overwrite is False.")
        for command in self.commands:
            if self.use_dependencies and (self.directory / command.creates).is_file():
                # This file already exists, we don't need to create it again
                continue
            yield command

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def as_bash_array(self) -> str:
        """Return a representation as a bash array.

        This creates a string formatted as a bash array containing all the commands in the job.

        """
        return_string = "( \\\n"
        for command in self:
            return_string += '"' + str(command) + '" \\\n'
        return_string += ")"
        return return_string
