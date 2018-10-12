#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Generate pbs files for submission on batch systems.

This will generate a .pbs file with all the information required to run a single command
from the list of commands. The variables will be generated and iterated over using the
job array feature of pbs. """

import logging
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List, Union

from .commands import Job

logger = logging.getLogger(__name__)


SCHEDULER_TEMPLATE = """
cd "{workdir}"
{setup}

COMMAND={command_list}

${{COMMAND[{array_index}]}}
"""


class SchedulerOptions:
    prefix: str = "#SHELL"
    name: str = "Experi-Job"
    resources: OrderedDict
    time: OrderedDict
    project: str = None
    log_dir: str = None
    email: str = None
    leftovers: OrderedDict

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in ["name", "N"]:
                self.name = value

            elif key in ["select", "nodes"]:
                self.resources["select"] = value
            elif key in ["ncpus", "cpus"]:
                self.resources["ncpus"] = value
            elif key in ["mem", "memory"]:
                self.resources["memory"] = value
            elif key in ["gpus", "ngpus"]:
                self.resources["ngpus"] = value

            elif key in ["walltime", "cputime"]:
                self.time[key] = value

            elif key in ["project", "account"]:
                self.project = value
            elif key in ["log", "logs", "output", "o"]:
                self.log_dir = value
            elif key in ["email", "mail"]:
                if isinstance(value, list):
                    self.email = ",".join(value)
                else:
                    self.email = value
            else:
                self.leftovers[key] = value

    def get_resources(self) -> str:
        resource_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.resources.items()]
        )
        return "{} Resources: {}\n".format(self.prefix, resource_str)

    def get_times(self) -> str:
        time_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.time.items()]
        )
        return "{} Time Resources: {}\n".format(self.prefix, time_str)

    def get_project(self) -> str:
        return "{} Project: {}\n".format(self.prefix, self.project)

    def get_logging(self) -> str:
        return "{} Log: {}\n".format(self.prefix, self.log_dir)

    def get_arbitrary_keys(self) -> str:
        output = ""
        for key, val in self.leftovers.items():
            output += "{} {}: {}\n".format(self.prefix, key, val)

        return output

    def get_name(self) -> str:
        return "{} Name: {}\n".format(self.prefix, self.name)

    def get_mail(self) -> str:
        return "{} Email: {}".format(self.prefix, self.email)

    def create_header(self) -> str:
        header_string = "#!/bin/bash\n"

        header_string += self.get_name()
        header_string += self.get_resources()
        header_string += self.get_times()
        header_string += self.get_logging()
        header_string += self.get_mail()
        header_string += self.get_arbitrary_keys()


class PBSOptions(SchedulerOptions):
    prefix = "#PBS"

    def get_resources(self) -> str:
        resource_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.resources.items()]
        )
        return "{} -l {}\n".format(self.prefix, resource_str)

    def get_times(self) -> str:
        time_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.time.items()]
        )
        return "{} -l {}\n".format(self.prefix, time_str)

    def get_project(self) -> str:
        if self.project:
            return "{} -P {}\n".format(self.prefix, self.project)
        return ""

    def get_logging(self) -> str:
        if self.log_dir:
            log_str = "{} -o {}\n".format(self.prefix, self.log_dir)
            # Join the output and the error to the one file
            # This is what I would consider a sensible default value since it is the
            # same as what you would see in the terminal and is the default behaviour in
            # slurm
            log_str += "{} -j oe\n".format(self.prefix)
            return log_str

        return ""

    def get_arbitrary_keys(self) -> str:
        output = ""
        for key, val in self.leftovers.items():
            if len(key) > 1:
                output += "{} --{} {}\n".format(self.prefix, key, val)
            else:
                output += "{} -{} {}\n".format(self.prefix, key, val)

        return output

    def get_name(self) -> str:
        return "{} -N {}\n".format(self.prefix, self.name)

    def get_mail(self) -> str:
        if self.email:
            email_str = "{} -M {}".format(self.prefix, self.email)
            # Email when the job is finished
            # This is a sensible default value, providing a notification in the form of
            # an email when a job is complete and further investigation is required.
            email_str += "{} -m ae".format(self.prefix)
            return email_str


class SLURMOptions(SchedulerOptions):
    prefix = "#SBATCH"

    def get_resources(self) -> str:
        resource_str = "{} --cpus-per-task {}".format(
            self.prefix, self.resources.get("ncpus")
        )
        if self.resources.get("memory"):
            resource_str += "{} --mem-per-task {}".format(
                self.prefix, self.resources["memory"]
            )
        if self.resources.get("ngpus"):
            resource_str += "{} --gres=gpu:{}".format(
                self.prefix, self.resources["ngpus"]
            )

        return resource_str

    def get_times(self) -> str:
        return "{} --time {}".format(self.prefix, self.time.get("walltime"))

    def get_project(self) -> str:
        if self.project:
            return "{} --account {}\n".format(self.prefix, self.project)
        return ""

    def get_logging(self) -> str:
        if self.log_dir:
            log_str = "{} --output {}/slurm-%A_%a.out\n".format(
                self.prefix, self.log_dir
            )
            return log_str

        return ""

    def get_arbitrary_keys(self) -> str:
        output = ""
        for key, val in self.leftovers.items():
            if len(key) > 1:
                output += "{} --{} {}\n".format(self.prefix, key, val)
            else:
                output += "{} -{} {}\n".format(self.prefix, key, val)

        return output

    def get_name(self) -> str:
        return "{} --name {}\n".format(self.prefix, self.name)


def parse_setup(options: Union[List, str]) -> str:
    """Convert potentially a list of commands into a single string.

    This creates a single string with newlines between each element of the list
    so that they will all run after each other in a bash script.

    """
    if isinstance(options, str):
        return options
    return "\n".join(options)


def create_header_string(scheduler: str, **kwargs) -> str:
    if scheduler == "PBS":
        return PBSOptions(**kwargs).create_header()
    if scheduler == "SLURM":
        return SLURMOptions(**kwargs).create_header()
    raise ValueError("Scheduler needs to be one of PBS or SLURM.")


def create_scheduler_file(job: Job) -> str:
    """Substitute values into a template scheduler file."""

    if job.scheduler_options is None:
        scheduler_options: Dict[str, Any] = {}
    else:
        scheduler_options = deepcopy(job.scheduler_options)
    try:
        setup_string = parse_setup(scheduler_options["setup"])
        del scheduler_options["setup"]
    except KeyError:
        setup_string = ""
    # Create header
    header_string = create_header_string(scheduler_options)

    num_commands = len(job)
    logger.debug("Number of commands: %d", num_commands)
    if num_commands > 1:
        header_string += "#PBS -J 0-{}\n".format(num_commands - 1)
    else:
        header_string += "PBS_ARRAY_INDEX=0\n"
    return header_string + SCHEDULER_TEMPLATE.format(
        workdir=r"$PBS_O_WORKDIR",
        command_list=job.as_bash_array(),
        setup=setup_string,
        array_index=r"$PBS_ARRAY_INDEX",
    )


def create_slurm_file(job: Job) -> str:
    """Substitute values into a template pbs file.

    This substitues the values in the pbs section of the input file
    into a simple template pbs file. Values not specified will use
    default options.

    """
    if job.scheduler_options is None:
        scheduler_options: Dict[str, Any] = {}
    else:
        scheduler_options = deepcopy(job.scheduler_options)
    try:
        setup_string = scheduler_options["setup"]
        del scheduler_options["setup"]
    except KeyError:
        setup_string = ""
    # Create header
    header_string = slurm_header(**scheduler_options)

    num_commands = len(job)
    logger.debug("Number of commands: %d", num_commands)
    if num_commands > 1:
        header_string += "#SBATCH -J 0-{}\n".format(num_commands - 1)
    else:
        header_string += "SLURM_ARRAY_TASK_ID=0\n"
    return header_string + SCHEDULER_TEMPLATE.format(
        workdir=r"$SLURM_SUBMIT_DIR",
        array_index=r"$SLURM_ARRAY_TASK_ID",
        command_list=job.as_bash_array(),
        setup=setup_string,
    )
