Experi
======

A framework for running command line applications with a range of different
variables.

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
experiment in the `experiment.yml` file. For details on setting up this file,
there are examples available in the [examples directory][experiment examples]
and documentation available [here][experiment docs].

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

What about ...?
---------------------

 - [Sumatra][] is a tool for managing and tracking projects,
    with a focus on running a single experiment at a time and the
    reproducibility of the results. Experi is more about running many
    simulations with a range of parameters, the reproducibility aspect is
    a byproduct of the way these parameters are specified. Also Sumatra does
    a much better job of the reproducibility than experi, capturing version
    numbers and executable paths.

- [SciPipe][] Is a workflow manager similar to [SciLuigi][], [Airflow][] or any
    number of other examples. These tools can be incredibly powerful,
    specifying complex networks of dependent tasks and managing their
    completion. However, they have a learning curve and can be difficult to
    configure with a task scheduler on a HPC. Experi is about simplicity;
    taking the workflow you already use and making it more powerful. Experi
    also uses the task scheduler for the management of dependent jobs, albeit
    the functionality is currently very basic.


Installation
------------

Experi is tested on python 3.4+ although 3.6+ is recommended #14.

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

[miniconda installer]: https://conda.io/miniconda.html
[Sumatra]: http://sumatra.readthedocs.io
[SciPipe]: http://scipipe.org/
[SciLuigi]: https://github.com/pharmbio/sciluigi
[Airflow]: https://airflow.apache.org/
[experiment examples]: https://github.com/malramsay64/experi/tree/master/examples
[experiment docs]: https://github.com/malramsay64/experi/blob/master/input_file.md
