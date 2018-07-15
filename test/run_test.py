#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the running of commands."""

from pathlib import Path
from typing import Iterator

import pytest

from experi.commands import Command, Job
from experi.run import process_scheduler, run_bash_jobs


@pytest.fixture
def create_jobs():

    def _create_jobs(command: str) -> Iterator[Job]:
        yield Job([Command(command)])

    return _create_jobs


@pytest.mark.parametrize(
    "command",
    [
        "false || mkdir passed",
        "mkdir passed || mkdir failed",
        "true && mkdir passed",
        "true && {{ false || mkdir passed; }}",
        "echo 'hello world' > passed",
        "echo -e 'hello world\ntest' > passed",
        "if [ 1 -eq 1 ]; then touch passed; fi",
        """
            if [ 0 -eq 1 ]; then
                touch failed
            else
                touch passed
            fi
        """,
    ],
)
def test_bash_operators(tmp_dir, create_jobs, command):
    """Test bash operators work.

    The commands are structured to create a file or directory "passed" when upon sucess.

    """
    jobs = create_jobs(command)
    run_bash_jobs(jobs, tmp_dir)
    assert (tmp_dir / "passed").exists()
    assert not (tmp_dir / "failed").exists()


@pytest.mark.parametrize(
    "structure",
    [
        {"result": "shell"},
        {"shell": True, "result": "shell"},
        {"shell": False, "pbs": "true", "result": "pbs"},
        {"shell": False, "pbs": False, "result": "shell"},
    ],
)
def test_process_scheduler(structure):
    assert process_scheduler(structure) == structure["result"]
