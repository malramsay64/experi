#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Generate scheduler files for submission on batch systems.

This will generate a .pbs file with all the information required to run a single command
from the list of commands. The variables will be generated and iterated over using the
job array feature of pbs. """

import logging
from pathlib import Path
from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List, Union

from .commands import Job

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


SCHEDULER_TEMPLATE = """
cd "{workdir}"
{setup}

COMMAND={command_list}

echo "${{COMMAND[{array_index}]}}"
${{COMMAND[{array_index}]}}
"""


class SchedulerOptions(ABC):
    name: str = "Experi_Job"
    resources: OrderedDict
    time: OrderedDict
    project: str = ""
    log_dir: str = ""
    email: str = ""
    leftovers: OrderedDict

    def __init__(self, **kwargs) -> None:
        # Initialise data structures with default values
        self.resources = OrderedDict(select=1, ncpus=1)
        self.time = OrderedDict(walltime="1:00")
        self.leftovers = OrderedDict()

        for key, value in kwargs.items():
            if key in ["name"]:
                self.name = value

            elif key in ["select", "nodes"]:
                self.resources["select"] = value
            elif key in ["ncpus", "cpus"]:
                self.resources["ncpus"] = value
            elif key in ["mem", "memory"]:
                self.resources["mem"] = value
            elif key in ["gpus", "ngpus"]:
                self.resources["ngpus"] = value

            elif key in ["walltime", "cputime"]:
                self.time[key] = value

            elif key in ["project", "account"]:
                self.project = value
            elif key in ["log", "logs", "output"]:
                self.log_dir = value
                log_path = Path(self.log_dir)
                if not log_path.exists():
                    logger.info(
                        "Logging directory %s does not exist, creating", log_path
                    )
                    log_path.mkdir()
            elif key in ["email", "mail"]:
                if isinstance(value, list):
                    self.email = ",".join(value)
                else:
                    self.email = value
            else:
                self.leftovers[key] = value

    def create_header(self) -> str:
        header_string = "#!/bin/bash\n"

        header_string += self.get_name()
        header_string += self.get_resources()
        header_string += self.get_project()
        header_string += self.get_times()
        header_string += self.get_logging()
        header_string += self.get_mail()
        header_string += self.get_arbitrary_keys()
        return header_string

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_resources(self):
        pass

    @abstractmethod
    def get_project(self):
        pass

    @abstractmethod
    def get_times(self):
        pass

    @abstractmethod
    def get_logging(self):
        pass

    @abstractmethod
    def get_mail(self):
        pass

    @abstractmethod
    def get_arbitrary_keys(self):
        pass


class ShellOptions(SchedulerOptions):
    def get_resources(self) -> str:
        resource_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.resources.items()]
        )
        return "#SHELL Resources: {}\n".format(resource_str)

    def get_times(self) -> str:
        time_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.time.items()]
        )
        return "#SHELL Time Resources: {}\n".format(time_str)

    def get_project(self) -> str:
        return "#SHELL Project: {}\n".format(self.project)

    def get_logging(self) -> str:
        return "#SHELL Log: {}\n".format(self.log_dir)

    def get_arbitrary_keys(self) -> str:
        output = ""
        for key, val in self.leftovers.items():
            output += "#SHELL {}: {}\n".format(key, val)

        return output

    def get_name(self) -> str:
        return "#SHELL Name: {}\n".format(self.name)

    def get_mail(self) -> str:
        if self.email:
            return "#SHELL Email: {}\n".format(self.email)
        return ""

    def create_header(self) -> str:
        header_string = "#!/bin/bash\n"

        header_string += self.get_name()
        header_string += self.get_resources()
        header_string += self.get_times()
        header_string += self.get_project()
        header_string += self.get_logging()
        header_string += self.get_mail()
        header_string += self.get_arbitrary_keys()
        return header_string


class PBSOptions(SchedulerOptions):
    def get_resources(self) -> str:
        resource_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.resources.items()]
        )
        return "#PBS -l {}\n".format(resource_str)

    def get_times(self) -> str:
        time_str = ":".join(
            ["{}={}".format(key, val) for key, val in self.time.items()]
        )
        return "#PBS -l {}\n".format(time_str)

    def get_project(self) -> str:
        if self.project:
            return "#PBS -P {}\n".format(self.project)
        return ""

    def get_logging(self) -> str:
        if self.log_dir:
            log_str = "#PBS -o {}\n".format(self.log_dir)
            # Join the output and the error to the one file
            # This is what I would consider a sensible default value since it is the
            # same as what you would see in the terminal and is the default behaviour in
            # slurm
            log_str += "#PBS -j oe\n"
            return log_str

        return ""

    def get_arbitrary_keys(self) -> str:
        output = ""
        for key, val in self.leftovers.items():
            if len(key) > 1:
                output += "#PBS --{} {}\n".format(key, val)
            else:
                output += "#PBS -{} {}\n".format(key, val)

        return output

    def get_name(self) -> str:
        return "#PBS -N {}\n".format(self.name)

    def get_mail(self) -> str:
        if self.email:
            email_str = "#PBS -M {}\n".format(self.email)
            # Email when the job is finished
            # This is a sensible default value, providing a notification in the form of
            # an email when a job is complete and further investigation is required.
            email_str += "#PBS -m ae\n"
            return email_str
        return ""


class SLURMOptions(SchedulerOptions):
    def get_resources(self) -> str:
        resource_str = "#SBATCH --cpus-per-task {}\n".format(
            self.resources.get("ncpus")
        )
        if self.resources.get("mem"):
            resource_str += "#SBATCH --mem-per-task {}\n".format(self.resources["mem"])
        if self.resources.get("ngpus"):
            resource_str += "#SBATCH --gres=gpu:{}\n".format(self.resources["ngpus"])

        return resource_str

    def get_times(self) -> str:
        return "#SBATCH --time {}\n".format(self.time["walltime"])

    def get_project(self) -> str:
        if self.project:
            return "#SBATCH --account {}\n".format(self.project)
        return ""

    def get_logging(self) -> str:
        if self.log_dir:
            log_str = "#SBATCH --output {}/slurm-%A_%a.out\n".format(self.log_dir)
            return log_str

        return ""

    def get_arbitrary_keys(self) -> str:
        output = ""
        for key, val in self.leftovers.items():
            if len(key) > 1:
                output += "#SBATCH --{} {}\n".format(key, val)
            else:
                output += "#SBATCH -{} {}\n".format(key, val)

        return output

    def get_name(self) -> str:
        return "#SBATCH --job-name {}\n".format(self.name)

    def get_mail(self) -> str:
        if self.email:
            email_str = "#SBATCH --mail-user {}\n".format(self.email)
            # Email when the job is finished
            # This is a sensible default value, providing a notification in the form of
            # an email when a job is complete and further investigation is required.
            email_str += "#SBATCH --mail-type END,FAIL\n"
            return email_str
        return ""


def parse_setup(options: Union[List, str]) -> str:
    """Convert potentially a list of commands into a single string.

    This creates a single string with newlines between each element of the list
    so that they will all run after each other in a bash script.

    """
    if isinstance(options, str):
        return options
    return "\n".join(options)


def create_header_string(scheduler: str, **kwargs) -> str:
    assert isinstance(scheduler, str)
    if scheduler.upper() == "PBS":
        return PBSOptions(**kwargs).create_header()
    if scheduler.upper() == "SLURM":
        return SLURMOptions(**kwargs).create_header()
    raise ValueError("Scheduler needs to be one of PBS or SLURM.")


def get_array_string(scheduler: str, num_commands: int) -> str:
    if scheduler.upper() == "SLURM":
        if num_commands > 1:
            header_string = "#SBATCH -J 0-{}\n".format(num_commands - 1)
        else:
            header_string = "SLURM_ARRAY_TASK_ID=0\n"
    elif scheduler.upper() == "PBS":
        if num_commands > 1:
            header_string = "#PBS -J 0-{}\n".format(num_commands - 1)
        else:
            header_string = "PBS_ARRAY_INDEX=0\n"
    else:
        raise ValueError("scheduler not recognised, must be one of [pbs|slurm]")
    return header_string


def create_scheduler_file(scheduler: str, job: Job) -> str:
    """Substitute values into a template scheduler file."""
    logger.debug("Create Scheduler File Function")

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
    header_string = create_header_string(scheduler, **scheduler_options)
    header_string += get_array_string(scheduler, len(job))

    if scheduler.upper() == "SLURM":
        workdir = r"$SLURM_SUBMIT_DIR"
        array_index = r"$SLURM_ARRAY_TASK_ID"
    elif scheduler.upper() == "PBS":
        workdir = r"$PBS_O_WORKDIR"
        array_index = r"$PBS_ARRAY_INDEX"

    return header_string + SCHEDULER_TEMPLATE.format(
        workdir=workdir,
        command_list=job.as_bash_array(),
        setup=setup_string,
        array_index=array_index,
    )
