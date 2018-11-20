#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test CLI interaction."""

import textwrap
from pathlib import Path

import pkg_resources
import pytest
from click.testing import CliRunner

from experi.run import main


@pytest.fixture
def runner():
    yield CliRunner()


def test_version(runner):
    result = runner.invoke(main, ["--version"])
    version = pkg_resources.get_distribution("experi").version
    assert version in result.output


def test_missing_input_file(runner):
    """Ensure error is raised when input file doesn't exist.

    This should occur both when a file is not specified, and when a file is specified.

    """
    with runner.isolated_filesystem():
        result = runner.invoke(main)
        assert result.exit_code != 0
        result = runner.invoke(main, ["-f", "nonexistant_file.yml"])
        assert result.exit_code != 0


@pytest.fixture()
def test_file(request):
    return textwrap.dedent(
        f"""
        jobs:
          - command:
              cmd: echo contents > {{creates}}
              creates: test.out

        variables:
            var1: 0
    """
    )


@pytest.mark.parametrize("scheduler", ["pbs", "slurm", "shell"])
def test_dry_run(runner, test_file, scheduler):
    with runner.isolated_filesystem():
        with open("experiment.yml", "w") as dst:
            dst.write(test_file)

        result = runner.invoke(main, ["--dry-run", "--scheduler", scheduler])
        print(result)
        assert result.exit_code == 0, result.exception

        if scheduler == "pbs":
            print(result.output)
            assert "qsub" in result.output
            assert Path("experi_00.pbs").is_file()
        elif scheduler == "shell":
            print(result.output)
            assert "bash -c" in result.output
            assert not Path("experi_00.pbs").is_file()
        elif scheduler == "slurm":
            assert "sbatch" in result.output
            assert Path("experi_00.slurm").is_file()
