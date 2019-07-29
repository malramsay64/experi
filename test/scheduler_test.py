#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.
#
# pylint: disable=redefined-outer-name

"""Test the building of scheduler files."""

import pytest

from experi.commands import Command, Job
from experi.run import process_structure, read_file, run_jobs
from experi.scheduler import (
    PBSOptions,
    ShellOptions,
    SLURMOptions,
    create_scheduler_file,
)

DEFAULT_PBS = """#!/bin/bash
#PBS -N Experi_Job
#PBS -l select=1:ncpus=1
#PBS -l walltime=1:00
PBS_ARRAY_INDEX=0

cd "$PBS_O_WORKDIR"


COMMAND=( \\
"echo 1" \\
)

echo "${COMMAND[$PBS_ARRAY_INDEX]}"
${COMMAND[$PBS_ARRAY_INDEX]}
"""

DEFAULT_SLURM = """#!/bin/bash
#SBATCH --job-name Experi_Job
#SBATCH --cpus-per-task 1
#SBATCH --time 1:00
SLURM_ARRAY_TASK_ID=0

cd "$SLURM_SUBMIT_DIR"


COMMAND=( \\
"echo 1" \\
)

echo "${COMMAND[$SLURM_ARRAY_TASK_ID]}"
${COMMAND[$SLURM_ARRAY_TASK_ID]}
"""


@pytest.mark.parametrize(
    "job, result",
    [
        (Job([Command("echo 1")]), '( \\\n"echo 1" \\\n)'),
        (
            Job([Command("echo 1"), Command("echo 2")]),
            '( \\\n"echo 1" \\\n"echo 2" \\\n)',
        ),
    ],
    ids=["single", "list"],
)
def test_jobs_as_bash_array(job, result):
    assert job.as_bash_array() == result


@pytest.mark.parametrize(
    "scheduler, expected",
    [("pbs", DEFAULT_PBS), ("slurm", DEFAULT_SLURM)],
    ids=["PBS", "SLURM"],
)
def test_default_files(scheduler, expected):
    assert create_scheduler_file(scheduler, Job([Command("echo 1")])) == expected


@pytest.mark.parametrize("scheduler", ["pbs", "slurm"])
def test_scheduler_creation(tmp_dir, scheduler):
    structure = read_file("test/data/scheduler/experiment.yml")
    jobs = process_structure(structure, scheduler=scheduler)
    run_jobs(jobs, scheduler, tmp_dir)
    expected = structure["result"][scheduler]
    with (tmp_dir / f"experi_00.{scheduler}").open("r") as result:
        assert result.read().strip() == expected.strip()


@pytest.fixture(params=["pbs", "slurm", "shell"])
def scheduler(request):
    schedulers = {"pbs": PBSOptions, "slurm": SLURMOptions, "shell": ShellOptions}
    return schedulers.get(request.param)


class TestHeader:
    def test_project(self, scheduler):
        project_name = "My Project"
        sched = scheduler(project=project_name)
        assert project_name in sched.create_header()

    def test_mail(self, scheduler):
        email = "email@example.com"
        sched = scheduler(mail=email)
        assert email in sched.create_header()
