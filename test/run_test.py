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
from experi.run import determine_scheduler, launch, run_bash_jobs


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
    assert determine_scheduler(None, structure) == structure["result"]


def test_dependencies(tmp_dir):
    command = Command(cmd="echo contents > {creates}", creates="test")
    jobs = [Job([command], directory=Path(tmp_dir), use_dependencies=True)]
    create_file = tmp_dir / "test"
    create_file.write_text("success")

    run_bash_jobs(jobs, tmp_dir)
    assert "success" in create_file.read_text()

    jobs[0].use_dependencies = False
    run_bash_jobs(jobs, tmp_dir)
    assert "contents" in create_file.read_text()


def test_dependencies_list(tmp_dir):
    commands = [
        Command(cmd=f"echo contents{i} > {{creates}}", creates=f"test{i}")
        for i in range(5)
    ]
    jobs = [Job(commands, directory=Path(tmp_dir), use_dependencies=True)]
    create_files = [tmp_dir / f"test{i}" for i in range(5)]

    create_files[1].write_text("success")

    run_bash_jobs(jobs, tmp_dir)
    for i in range(5):
        if i == 1:
            assert "success" in create_files[i].read_text()
        else:
            assert f"contents{i}" in create_files[i].read_text()


def test_dry_run(tmp_dir):
    command = Command(cmd="echo contents > {creates}", creates="test")
    jobs = [Job([command], directory=Path(tmp_dir))]
    create_file = tmp_dir / "test"
    run_bash_jobs(jobs, tmp_dir, dry_run=True)
    assert not create_file.exists()


@pytest.mark.parametrize("scheduler", ["pbs", "slurm", "shell"])
@pytest.mark.parametrize("dry_run", [True, False])
@pytest.mark.parametrize("use_dependencies", [True, False])
def test_launch(scheduler, dry_run, use_dependencies):
    launch("test/data/experiment.yml", use_dependencies, dry_run, scheduler)
