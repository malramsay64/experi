.. experi documentation master file, created by
   sphinx-quickstart on Mon Jul 16 14:13:44 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to experi's documentation!
==================================

When running a series of experiments it can be difficult to remember the exact parameters of the
experiment, or even how to run the simulation again. Additionally for complex experiments with many
variables, iterating through all the combinations of variables can be unwieldy, error prone, and
frustrating to write.

Experi keeps all the information to run an experiment in an ``experiment.yml`` file which resides in
the same directory as the experimental results. This makes it possible to version control the
experiment through the ``experiment.yml``` file. Experi supports complex iteration of variables
defined in a human readable yaml syntax, making it simple to understand the experimental conditions
defined within. Having an easy to understand definition of the experimental conditions also provides
a reference when coming back to look at the results.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    installation



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
