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


PBS_TEMPLATE = """
cd "$PBS_O_WORKDIR"
{setup}

COMMAND={command_list}

${{COMMAND[$PBS_ARRAY_INDEX]}}
"""


def parse_setup(options: Union[List, str]) -> str:
    """Convert potentially a list of commands into a single string.

    This creates a single string with newlines between each element of the list
    so that they will all run after each other in a bash script.

    """
    if isinstance(options, str):
        return options
    return "\n".join(options)


def pbs_header(**kwargs):
    """Parse arbitrary pbs options into a header."""
    header_string = "#!/bin/bash\n"

    # Parse name
    if kwargs.get("N"):
        header_string += "#PBS -N {}\n".format(kwargs.get("N").replace(" ", "_"))
        del kwargs["N"]
    elif kwargs.get("name"):
        header_string += "#PBS -N {}\n".format(kwargs.get("name").replace(" ", "_"))
        del kwargs["name"]
    else:
        header_string += "#PBS -N {}\n".format("experi")

    # Parse resources
    resources = OrderedDict()
    # set default values
    resources["select"] = 1
    resources["ncpus"] = 1
    # nodes
    if kwargs.get("select"):
        resources["select"] = kwargs.get("select")
        del kwargs["select"]
    elif kwargs.get("nodes"):
        resources["select"] = kwargs.get("nodes")
        del kwargs["nodes"]
    # cpus/node
    if kwargs.get("ncpus"):
        resources["ncpus"] = kwargs.get("ncpus")
        del kwargs["ncpus"]
    elif kwargs.get("cpus"):
        resources["ncpus"] = kwargs.get("cpus")
        del kwargs["cpus"]
    # memory
    if kwargs.get("mem"):
        resources["mem"] = kwargs.get("mem")
        del kwargs["mem"]
    elif kwargs.get("memory"):
        resources["mem"] = kwargs.get("memory")
        del kwargs["memory"]
    # gpus
    if kwargs.get("ngpus"):
        resources["ngpus"] = kwargs.get("ngpus")
        del kwargs["ngpus"]
    elif kwargs.get("ngpus"):
        resources["ngpus"] = kwargs.get("gpus")
        del kwargs["gpus"]
    # assemble string
    header_string += "#PBS -l {}\n".format(
        ":".join(["{}={}".format(key, val) for key, val in resources.items()])
    )

    # Parse times
    times = {"walltime": "1:00"}
    if kwargs.get("walltime"):
        times["walltime"] = kwargs.get("walltime")
        del kwargs["walltime"]

    if kwargs.get("cputime"):
        times["cputime"] = kwargs.get("cputime")
        del kwargs["cputime"]

    header_string += "#PBS -l {}\n".format(
        ":".join(["{}={}".format(key, val) for key, val in times.items()])
    )

    # Parse project
    if kwargs.get("P"):
        header_string += "#PBS -P {}\n".format(kwargs.get("P"))
        del kwargs["P"]
    elif kwargs.get("project"):
        header_string += "#PBS -P {}\n".format(kwargs.get("project"))
        del kwargs["project"]

    # Parse arbitrary options
    for key, val in kwargs.items():
        logger.warning("Arbitrary key passed: -%s %s", key, val)
        header_string += "#PBS -{} {}\n".format(key, val)

    return header_string


def create_pbs_file(job: Job) -> str:
    """Substitute values into a template pbs file.

    This substitutes the values in the pbs section of the input file
    into a simple template pbs file. Values not specified will use
    default options.

    """
    if job.scheduler_options is None:
        pbs_options: Dict[str, Any] = {}
    else:
        pbs_options = deepcopy(job.scheduler_options)
    try:
        setup_string = parse_setup(pbs_options["setup"])
        del pbs_options["setup"]
    except KeyError:
        setup_string = ""
    # Create header
    header_string = pbs_header(**pbs_options)

    num_commands = len(job)
    logger.debug("Number of commands: %d", num_commands)
    if num_commands > 1:
        header_string += "#PBS -J 0-{}\n".format(num_commands - 1)
    else:
        header_string += "PBS_ARRAY_INDEX=0\n"
    return header_string + PBS_TEMPLATE.format(
        command_list=job.as_bash_array(), setup=setup_string
    )
