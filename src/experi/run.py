#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Run an experiment varying a number of variables."""

import logging
import os
import shutil
import subprocess
import sys
from collections import ChainMap
from itertools import chain, product, repeat
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Union

import click
import numpy as np
import yaml

from .commands import Command, Job
from .pbs import create_pbs_file

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

# Type definitions
PathLike = Union[str, Path]
YamlValue = Union[str, int, float]
CommandInput = Union[str, Dict[str, YamlValue]]
VarType = Union[YamlValue, List[YamlValue], Dict[str, YamlValue]]
VarMatrix = List[Dict[str, YamlValue]]


def combine_dictionaries(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge a list of dictionaries into a single dictionary.

    Where there are collisions the first value in the list will be set
    as this function is using ChainMap to combine the dicts.

    """
    return dict(ChainMap(*dicts))


def iterator_zip(variables: VarType, parent: str = None) -> Iterable[VarMatrix]:
    """Apply the zip operator to a set of variables.

    This uses the python zip iterator to combine multiple lists of variables such that
    the nth variable in each list is aligned.

    Args:
        variables: The variables object
        parent: Unused

    """

    logger.debug("Yielding from zip iterator")
    if isinstance(variables, list):
        for item in variables:
            yield list(variable_matrix(item, parent, "zip"))
    else:
        yield list(variable_matrix(variables, parent, "zip"))


def iterator_product(variables: VarType, parent: str = None) -> Iterable[VarMatrix]:
    """Apply the product operator to a set of variables.

    This uses the python itertools.product iterator to combine multiple variables
    such that all possible combinations are generated. This is the default iterator
    however this is a method of manually specifying the option.

    Args:
        variables: The variables object
        parent: Unused

    """
    logger.debug("Yielding from product iterator")
    if isinstance(variables, list):
        raise ValueError(
            f"Product only takes mappings of values, got {variables} of type {type(variables)}"
        )

    yield list(variable_matrix(variables, parent, "product"))


def iterator_chain(variables: VarType, parent: str = None) -> Iterable[VarMatrix]:
    """This successively appends each element of an array to a single list of values.

    This takes a list of values and puts all the values generated for each element in
    the list into a single list of values. It uses the :func:`itertools.chain` function to
    achieve this. This function is particularly useful for specifying multiple types of
    simulations with different parameters.

    Args:
        variables: The variables object
        parent: Unused

    """
    logger.debug("Yielding from append iterator")
    if not isinstance(variables, list):
        raise ValueError(
            f"Append keyword only takes a list of arguments, got {variables} of type {type(variables)}"
        )

    # Create a single list containing all the values
    yield list(
        chain.from_iterable(
            variable_matrix(item, parent, "product") for item in variables
        )
    )


def arange(start=None, stop=None, step=None, dtype=None) -> np.ndarray:
    if stop and not start:
        return np.arange(stop)
    return np.arange(start=start, stop=stop, step=step, dtype=dtype)


def iterator_arange(variables: VarType, parent: str) -> Iterable[VarMatrix]:
    """Create a list of values using the :func:`numpy.arange` function.

    Args:
        variables: The input variables for the creation of the range
        parent: The variable for which the values are being generated.

    Returns: A list of dictionaries mapping the parent to each value.

    """
    assert parent is not None
    if isinstance(variables, (int, float)):
        yield [{parent: i} for i in np.arange(variables)]

    elif isinstance(variables, dict):
        if variables.get("stop"):
            yield [{parent: i} for i in arange(**variables)]
        else:
            raise ValueError(f"Stop is a required keyword for the arange iterator.")

    else:
        raise ValueError(
            f"The arange keyword only takes a dict as arguments, got {variables} of type {type(variables)}"
        )


def iterator_cycle(variables: VarType, parent: str) -> Iterable[VarMatrix]:
    """Cycle through a list of values a specified number of times

    Args:
        variables: The input variables for the creation of the range
        parent: The variable for which the values are being generated.

    Returns: A list of dictionaries mapping the parent to each value.

    """
    if isinstance(variables, dict):
        if variables.get("times"):
            times = int(variables["times"])
            del variables["times"]

            yield list(variable_matrix(variables, parent, "product")) * times

        else:
            raise ValueError(f"times is a required keyword for the repeat iterator.")
    else:
        raise ValueError(
            f"The repeat operator only takes a dict as arguments, got {variables} of type {type(variables)}"
        )


def variable_matrix(
    variables: VarType, parent: str = None, iterator: str = "product"
) -> Iterable[Dict[str, YamlValue]]:
    """Process the variables into a list of the appropriate combinations.

    This function performs recursive processing of the input variables, creating an
    iterator which has all the combinations of variables specified in the input.

    """
    _iters: Dict[str, Callable] = {"product": product, "zip": zip}
    _special_keys: Dict[str, Callable[[VarType, Any], Iterable[VarMatrix]]] = {
        "zip": iterator_zip,
        "product": iterator_product,
        "arange": iterator_arange,
        "chain": iterator_chain,
        "append": iterator_chain,
        "cycle": iterator_cycle,
        "repeat": iterator_cycle,
    }

    if isinstance(variables, dict):
        key_vars: List[List[Dict[str, YamlValue]]] = []

        # Handling of specialised iterators
        for key, function in _special_keys.items():
            if variables.get(key):
                item = variables[key]
                assert item is not None
                for val in function(item, parent):
                    key_vars.append(val)

                del variables[key]

        for key, value in variables.items():
            key_vars.append(list(variable_matrix(value, key, iterator)))

        logger.debug("key vars: %s", key_vars)

        # Iterate through all possible products generating a dictionary
        for i in _iters[iterator](*key_vars):
            logger.debug("dicts: %s", i)
            yield combine_dictionaries(i)

    # Iterate through a list of values
    elif isinstance(variables, list):
        for item in variables:
            yield from variable_matrix(item, parent, iterator)

    # Stopping condition -> we have either a single value from a list
    # or a value had only one item
    else:
        assert parent is not None
        yield {parent: variables}


def uniqueify(my_list: Any) -> List[Any]:
    """Remove duplicate entries in a list retaining order."""
    if sys.version_info >= (3, 6):
        # An implementation specific detail of py3.6 is the retention of order
        # within a dictionary. In py3.7 this becomes the documented behaviour.
        return list(dict.fromkeys(my_list))

    # Slower method of order preserving unique list in older python versions
    seen = set()
    return [x for x in my_list if x not in seen and not seen.add(x)]


def process_jobs(
    jobs: List[Dict],
    matrix: VarMatrix,
    scheduler_options: Dict[str, Any] = None,
    directory: Path = None,
    use_dependencies: bool = False,
) -> Iterator[Job]:
    assert jobs is not None

    logger.debug("Found %d jobs in file", len(jobs))

    for job in jobs:
        command = job.get("command")
        assert command is not None
        yield Job(
            process_command(command, matrix),
            scheduler_options,
            directory,
            use_dependencies,
        )


def process_command(command: CommandInput, matrix: VarMatrix) -> List[Command]:
    """Generate all combinations of commands given a variable matrix.

    Processes the commands to be sequences of strings.

    """
    assert command is not None
    if isinstance(command, str):
        command_list = [Command(command, variables=variables) for variables in matrix]
    elif isinstance(command, list):
        command_list = [Command(command, variables=variables) for variables in matrix]
    else:
        if command.get("command") is not None:
            cmd = command.get("command")
        else:
            cmd = command.get("cmd")
        creates = str(command.get("creates", ""))
        requires = str(command.get("requires", ""))

        assert isinstance(cmd, (list, str))
        command_list = [
            Command(cmd, variables, creates, requires) for variables in matrix
        ]
    return uniqueify(command_list)


def read_file(filename: PathLike = "experiment.yml") -> Dict[str, Any]:
    """Read and parse yaml file."""
    logger.debug("Input file: %s", filename)

    with open(filename, "r") as stream:
        structure = yaml.safe_load(stream)
    return structure


def process_structure(
    structure: Dict[str, Any],
    scheduler: str = "shell",
    directory: Path = None,
    use_dependencies: bool = False,
) -> Iterator[Job]:
    input_variables = structure.get("variables")
    if input_variables is None:
        raise KeyError('The key "variables" was not found in the input file.')
    assert isinstance(input_variables, Dict)

    # create variable matrix
    variables = list(variable_matrix(input_variables))
    assert variables

    scheduler_options = None

    # Check for pbs options
    if structure.get(scheduler):
        scheduler_options = structure.get(scheduler)
        if scheduler_options is True:
            scheduler_options = {}
        assert isinstance(scheduler_options, dict)
        if structure.get("name"):
            # set the name attribute in pbs to global name if no name defined in pbs
            scheduler_options.setdefault("name", structure.get("name"))

    jobs_dict = structure.get("jobs")
    if jobs_dict is None:
        input_command = structure.get("command")
        if isinstance(input_command, list):
            jobs_dict = [{"command": cmd} for cmd in input_command]
        else:
            jobs_dict = [{"command": input_command}]

    yield from process_jobs(
        jobs_dict, variables, scheduler_options, directory, use_dependencies
    )


def run_jobs(
    jobs: Iterator[Job],
    scheduler: str = "shell",
    directory=Path.cwd(),
    dry_run: bool = False,
) -> None:
    if scheduler == "shell":
        run_bash_jobs(jobs, directory, dry_run=dry_run)
    elif scheduler == "pbs":
        run_pbs_jobs(jobs, directory, dry_run=dry_run)
    else:
        raise ValueError(
            f"Scheduler '{scheduler}'was not recognised. Possible values are ['shell', 'pbs']"
        )


def run_bash_jobs(
    jobs: Iterator[Job], directory: PathLike = Path.cwd(), dry_run: bool = False
) -> None:
    """Submit commands to the bash shell.

    This function runs the commands iteratively but handles errors in the
    same way as with the pbs_commands function. A command will run for all
    combinations of variables in the variable matrix, however if any one of
    those commands fails then the next command will not run.

    """
    logger.debug("Running commands in bash shell")
    # iterate through command groups
    for job in jobs:
        # Check shell exists
        if shutil.which(job.shell) is None:
            raise ProcessLookupError("The shell '{job.shell}' was not found.")

        failed = False
        for command in job:
            for cmd in command:
                logger.info(cmd)
                if dry_run:
                    print(f"{job.shell} -c '{cmd}'")
                else:
                    result = subprocess.run(
                        [job.shell, "-c", f"{cmd}"], cwd=str(directory)
                    )
                    if result.returncode != 0:
                        failed = True
                        logger.error("Command failed: %s", command)
                        break
        if failed:
            logger.error("A command failed, not continuing further.")
            return


def run_pbs_jobs(
    jobs: Iterator[Job],
    directory: PathLike = Path.cwd(),
    basename: str = "experi",
    dry_run: bool = False,
) -> None:
    """Submit a series of commands to a batch scheduler.

    This takes a list of strings which are the contents of the pbs files, writes the
    files to disk and submits the job to the scheduler. Files which match the pattern of
    the resulting files <basename>_<index>.pbs are deleted before writing the new files.

    To ensure that commands run consecutively the aditional requirement to the run
    script `-W depend=afterok:<prev_jobid>` is added. This allows for all the components
    of the experiment to be conducted in a single script.

    Note: Having this function submit jobs requires that the command `qsub` exists,
    implying that a job scheduler is installed.

    """
    submit_job = True
    logger.debug("Creating commands in pbs files.")
    # Check qsub exists
    if shutil.which("qsub") is None:
        logger.warning(
            "The `qsub` command is not found."
            "Skipping job submission and just generating files"
        )
        submit_job = False

    # Ensure directory is a Path
    directory = Path(directory)

    # remove existing files
    for fname in directory.glob(basename + "*.pbs"):
        print("Removing {}".format(fname))
        os.remove(str(fname))

    # Write new files and generate commands
    prev_jobids: List[str] = []
    for index, job in enumerate(jobs):
        # Generate pbs file
        content = create_pbs_file(job)
        # Write file to disk
        fname = Path(directory / "{}_{:02d}.pbs".format(basename, index))
        with fname.open("w") as dst:
            dst.write(content)

        if submit_job or dry_run:
            # Construct command
            submit_cmd = ["qsub"]

            if prev_jobids:
                # Continue to append all previous jobs to submit_cmd so subsequent jobs die along
                # with the first.
                submit_cmd += ["-W", "depend=afterok:{} ".format(":".join(prev_jobids))]

            # actually run the command
            logger.info(str(submit_cmd))
            try:
                if dry_run:
                    print(f"{submit_cmd} {fname.name}")
                    prev_jobids.append("dry_run")
                else:
                    cmd_res = subprocess.check_output(
                        submit_cmd + [fname.name], cwd=str(directory)
                    )
                    prev_jobids.append(cmd_res.decode().strip())
            except subprocess.CalledProcessError:
                logger.error("Submitting job to the queue failed.")
                break


def process_scheduler(structure: Dict[str, Any]) -> str:
    """Get the scheduler to run the jobs.

    Determine the shell to run the command from the input file. This checks for the
    presence of keys in the input file corresponding to the different schedulers. The
    schedulers that are supported are

    - shell, and
    - pbs

    listed in the order of precedence. The first scheduler with a truthy value in the
    input file is the value returned by this function. Where no truthy values are found
    the defualt value is "shell.

    """
    if structure.get("shell"):
        return "shell"
    if structure.get("pbs"):
        return "pbs"
    return "shell"


def _set_verbosity(ctx, param, value):
    if value == 1:
        logging.basicConfig(level=logging.INFO)
    if value == 2:
        logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.version_option()
@click.option(
    "-f",
    "--input-file",
    type=click.Path(exists=True, dir_okay=False),
    default="experiment.yml",
    help="""Path to a YAML file containing experiment data. Note that the experiment
    will be run from the directory in which the file exists, not the directory the
    script was run from.""",
)
@click.option(
    "--use-dependencies",
    default=False,
    is_flag=True,
    help="Use the dependencies specified in the command to reduce the processing",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Don't run commands or submit jobs, just show the commands that would be run.",
)
@click.option(
    "-v",
    "--verbose",
    callback=_set_verbosity,
    expose_value=False,
    count=True,
    help="Increase the verbosity of logging events.",
)
def main(input_file, use_dependencies, dry_run) -> None:
    # Process and run commands
    input_file = Path(input_file)
    structure = read_file(input_file)
    scheduler = process_scheduler(structure)
    jobs = process_structure(
        structure, scheduler, Path(input_file.parent), use_dependencies
    )
    run_jobs(jobs, scheduler, input_file.parent, dry_run)
