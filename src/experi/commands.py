#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Command class."""

from typing import Any, Dict, NamedTuple


class Command(object):
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
