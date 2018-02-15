#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the building of pbs files."""

from pathlib import Path

import pytest

from experi.pbs import commands2bash_array, create_pbs_file
from experi.run import process_file, read_file


DEFAULT_PBS = """#!/bin/bash
#PBS -N experi
#PBS -l select=1:ncpus=1
#PBS -l walltime=1:00
PBS_ARRAY_INDEX=0

cd "$PBS_O_WORKDIR"


COMMAND=( \\
"echo 1" \\
)

${COMMAND[$PBS_ARRAY_INDEX]}
"""


@pytest.mark.parametrize('command, result', [
    (['echo 1'], '( \\\n"echo 1" \\\n)'),
    (['echo 1', 'echo 2'], '( \\\n"echo 1" \\\n"echo 2" \\\n)')
])
def test_commands2bash(command, result):
    assert commands2bash_array(command) == result


def test_default_pbs():
    assert create_pbs_file(['echo 1'], {}) == DEFAULT_PBS


def test_pbs_creation():
    directory = Path('test/data/pbs')
    process_file(directory / 'experiment.yml')
    expected = read_file(directory / 'experiment.yml')['result']
    with (directory / 'experi_00.pbs').open('r') as result:
        assert result.read() == expected
