Experi
======


[![Build Status](https://travis-ci.org/malramsay64/experi.svg?branch=master)](https://travis-ci.org/malramsay64/experi)
[![codecov](https://codecov.io/gh/malramsay64/experi/branch/master/graph/badge.svg)](https://codecov.io/gh/malramsay64/experi)
![PyPI](https://img.shields.io/pypi/v/experi.svg)
[![Anaconda-Server Badge](https://anaconda.org/malramsay/experi/badges/version.svg)](https://anaconda.org/malramsay/experi)


A framework for running command line applications with a range of different
variables.

Documentation is available on [Read the Docs][Experi Docs]

How to use
----------

Actually running experi is a simple process, in a directory with an
`experiment.yml` file run the command

```
$ experi
```

If for whatever reason you want to name the file something other than
`experiment.yml` or to run a file in a different directory a custom file can be
specified with the `-f` flag

```
$ experi -f not_an_experiment.yml
```

Note that since this is designed to keep the specification of the experiment
with the results, the commands will be run in the same directory as the
specified file.

The complicated part of getting everything running is the specification of the
experiment in the `experiment.yml` file. The details on configuring this file is available in the
[documentation][Experi Docs input_file].

Why should I use this?
----------------------

When running a series of experiments it can be difficult to remember the exact
parameters of the experiment, or even how to run the simulation again.
Additionally for a complex experiment with many variables, iterating through
all the combinations of variables can be unwieldy, error prone, and plain
frustrating.

Experi aims to keep all the information about running an experiment in an
`experiment.yml` file which sits in the same directory as the experiment.
Supporting complex iteration of variables incorporated into easily the easily
readable yaml syntax, it is easy to quickly understand the experimental
conditions. Additionally by keeping the configuration file with the results
there is a quick reference to the experimental conditions and replication is as
simple as running `experi`.

For more information I have written a [blog post][experi blog post] which goes
into more depth on how this tool has helped my workflow.

Project Goals
-------------

The primary goals of this project detailed below. They act as the guiding
principles for the design decisions which are made.

- Human centric
  - Interactions should be simple, intuitive, and frictionless
  - Shouldn't need to constantly consult documentation to use
  - Minimal expertise required to understand

- Sensible Defaults
  - Testing a job on a scheduler should be simple, requiring a minimal specification

- Fast Errors
  - Errors in the code should be picked up as soon as possible, i.e. shouldn't arise
    after waiting in the job queue.
  - Allow for testing locally using the shell, before running on HPC

Where current functionality doesn't meet these goals please raise an issue, I am
more than happy to discuss. Although do note that these goals are somewhat
opinionated.

What about ...?
---------------------

- [Sumatra] is a tool for managing and tracking projects,
    with a focus on running a single experiment at a time and the
    reproducibility of the results. Experi is more about running many
    simulations with a range of parameters, the reproducibility aspect is
    a byproduct of the way these parameters are specified. Also Sumatra does
    a much better job of the reproducibility than experi, capturing version
    numbers and executable paths.

- [SciPipe] is a workflow manager similar to [SciLuigi], [Airflow] or any
    number of other examples. These tools can be incredibly powerful,
    specifying complex networks of dependent tasks and managing their
    completion. However, they have a learning curve and can be difficult to
    configure with a task scheduler on a HPC. Experi is about simplicity;
    taking the workflow you already use and making it more powerful. Experi
    also uses the task scheduler for the management of dependent jobs, albeit
    the functionality is currently very basic.

- [Snakemake] is a workflow management tool, very similar to [GNU Make] which
    supports submitting jobs to a HPC scheduler. I personally have no experience
    using it, however from reading the documentation it is a highly configurable
    tool with far more functionality than Experi. Experi is more suitable is the
    handling of complex specification of variables and using the scheduler for
    control of scheduling.


Installation
------------

Experi is currently compatible with python>==3.6

```bash
pip3 install experi
```

Note that for the command `experi` to work the directory containing the
executable needs to be in the `PATH` variable. In most cases this will probably
be `$HOME/.local/bin` although this is installation dependent. If you don't
know where the executable is, on \*nix systems the command

```bash
find $HOME -name experi
```

will search everywhere in your home directory to find it. Alternatively
replacing `$HOME` with `/` will search everywhere.

For installation from source

```bash
git clone https://github.com/malramsay64/experi.git
cd experi
pip3 install .
```

To install a development version, `pipenv` is required which can be installed
by running

```bash
pip3 install pipenv
```

and installing the dependencies by running

```bash
pipenv install --dev --three
```

which will create a virtual environment for the project. Activating the
virtualenv is can be done by running

```bash
pipenv shell
```

which creates a new shell with the environment activated. Alternatively
a single command (like the test cases) can be run using

```bash
pipenv run pytest
```

For those of you trying to run this on a cluster with only user privileges
including the `--user` flag will resolve issues with pip requiring elevated
permissions installing to your home directory rather than for everyone.

```
pip3 install --user experi
```

For more information documentation is available on [Read the Docs][Experi Docs].

[Experi Docs]: https://experi.readthedocs.io/en/latest/
[Experi Docs input_file]: https://experi.readthedocs.io/en/latest/input_file
[miniconda installer]: https://conda.io/miniconda.html
[Sumatra]: http://sumatra.readthedocs.io
[SciPipe]: http://scipipe.org/
[SciLuigi]: https://github.com/pharmbio/sciluigi
[Airflow]: https://airflow.apache.org/
[Snakemake]: https://snakemake.readthedocs.io/en/stable/
[GNU Make]: https://www.gnu.org/software/make/
[experiment examples]: https://github.com/malramsay64/experi/tree/master/examples
[experiment docs]: https://github.com/malramsay64/experi/blob/master/input_file.md
[experi blog post]: https://malramsay.com/post/experi_a_tool_for_computational_experiments/
