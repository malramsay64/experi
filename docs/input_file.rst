Input File Specification
========================

This document is a guide to the ``experiment.yml`` file which is used as the input file for
Experi. This file specifies all the parameters for running an experiment. The ``experiment.yml``
file is designed to be a human readable reference to the experimental data it generates; there is
no simple method of running the experiment from a different directory.

The ``experiment.yml`` file has three main sections each section having a different role in the
running of the experiment.

- The `command <#Commands>`__ section defines the shell commands to run the experiment.
- The `variables <#Variables>`__ section defines the variables to substitute into the commands.
- The `scheduler <#Scheduler>`__ section defines the scheduler to use and the associated options.

Experi uses the `YAML`_ file format for the input file since it has widespread use and support and
the format is simple for a human to parse. If you are unfamiliar with YAML have a look at `this
quick guide <YAML Guide>`_.

Commands
--------

The ``commands`` section is one of the main elements of the input file, specifying the commands to run
and how to run them. At it's simplest the command key is a bash command to execute as in the example
below.

.. code:: yaml

   # experiment.yml

   command: echo Hello World

The command key can also take a list of bash commands, executing each of the commands in order.

.. code:: yaml

   # experiment.yml

   command:
       - echo First Command
       - echo Second Command
       - echo Third Command

Variable Substitution
~~~~~~~~~~~~~~~~~~~~~

The power of Experi is taking a single command instance and replacing a variable with it's values
defined under the `variables <#variables>`_ key. Variables take the form of the new style python
string formatting, with variable names surrounded by braces --- ``{variable}`` will be replaced with
the value of ``variable``. For more information on these format strings the `python string
formatting documentation`_ is a reference guide, while `pyformat.info`_ is a guide to practical use.

In practice, using variables looks like this;

.. code:: yaml

    # experiment.yml

    command: echo {nth} Command

Unlike the previous example with a list, there is no guarantee of order for the commands to run.
Each combination of variables is effectively a separate command instance which could be running at
the same time as any other command instance. Where there is a dependence between tasks, like
creating a directory, passing a list to the command key has a guarantee on ordering.

.. code:: yaml

   # experiment.yml

   command:
       - mkdir -p {variable}
       - echo {variable} > {variable}/out.txt

In the above example, ``mkdir -p {variable}`` will always be executed before the file ``out.txt`` is
written in it.

There is no limit to the number of variables specified to a command however, variables specified in
a command need to have a definition in the variables key.

After variable substitution, only unique command objects are run, where uniqueness takes into account
all bash commands in a list. This is to allow for the over-specification of variables for certain
steps of more complicated workflows (see `Jobs <#Jobs>`_). The rationale for this choice is that
commands which are non-unique will typically have the same output, overwriting each other. Where
this is a problem, adding an ``echo {variable}`` to the list within a command key is a reasonable
workaround.


Command Failure
~~~~~~~~~~~~~~~

When running an array job on a scheduler every command in the array will run even if the first one
fails. This is the behaviour that Experi replicates for all environments it can run in. Every
combination of variables is executed, with a successful command meaning the exit code for all
variables was 0 (success), while if one combination of variables fails then the entire command is
considered to have failed.

Managing Complex Jobs
~~~~~~~~~~~~~~~~~~~~~

A common component of running an experiment is that the number of tasks changes at different points.
An experiment could consist of 3 steps;

1. An initial phase which generates some starting configurations,
2. A simulation phase which subjects the starting configurations to a large number experimental conditions,
3. An analysis phase which aggregates the data from the simulation phase

Here steps 1 and 3 might have a single set of variables, while step 2 has hundreds. Experi has the
``jobs`` keyword to facilitate these types of experiments.

.. code:: yaml

    jobs:
        - command: echo "Command 1"
        - command:
            - mkdir -p {var}
            - cd {var}
            - echo "Command 2 {var}"
        - command: echo "Command 3"

The jobs key allows you to break an experiment into a list of commands, with each separate command
being a different job on the scheduler. Each of command key is the same as described in the above
sections.

.. note::

    I should note that the command key will work fine when submitting a job to the scheduler, the above
    example can be expressed with a single command key

    .. code:: yaml

        command:
            1. echo "Command 1"
            2. mkdir -p {var}
            3. cd {var}
            4. echo "Command 2 {var}"
            5. echo "Command 3"

    The difference is that in the first example ``Command 1`` and ``Command 3`` are only echoed once,
    while in this example they are both echoed for each value of ``{var}``.

When using the jobs keyword, a prerequisite of executing the next set of commands is a successful
exit code of all shell commands executed in the current command key. This is making the assumption
that all experimental conditions are going to succeed and are required for the following steps. This
makes a lot of sense for a setup step, although less so for a search of parameter space where it is
likely to have numeric instabilities. I have an `open issue <experi #12>`_ to allow for the user
override of this feature, although a workaround in the meantime is to suffix commands which might
fail with ``|| true``. This is the *or* operator followed by a command which will always
succeed---another more informative alternative is to ``echo`` a message. This means that the return
value of the shell command always indicates success.

Variables
---------

This is where the real power of experi lies, in being able to specify complex sets of variables in a
simple human readable fashion. Variables are specified using the names as given in the command
section. The simplest case is for a single value of a variable

.. code:: yaml

    # experiment.yml

    command: echo hello {name}

    variables:
        name: Alice

Specifying lists of variables can be done in the same way as the commands, again for this simple
case,

.. code:: yaml

    variables:
        variable1:
            - Alice
            - Bob
            - Charmaine

Multiple Variables
~~~~~~~~~~~~~~~~~~

Specifying multiple variables is as simple as specifying a single variable, however by default, all
possible combinations of the variables are generated. In the simplest case, with just a single value
per variable

.. code:: yaml

    command: echo {greeting} {name}
    variables:
        greeting: hello
        name: Alice

the resulting of the command would be ``hello Alice``. To greet multiple people we just add more
names

.. code:: yaml

    comamnd: echo {greeting} {name}
    variables:
        greeting: hello
        name:
            - Alice
            - Bob
            - Charmaine

which would result in

.. code:: text

    hello Alice
    hello Bob
    hello Charmaine

We have all possible combinations of the greeting and the name. Extending this, to greet all the
people in both English and French we can add both the greetings, and all the names giving the input
file

.. code:: yaml

    command: echo {greeting} {name}
    variables:
        greeting:
            - hello
            - bonjour
        name:
            - Alice
            - Bob
            - Charmaine

and resulting in the output

.. code:: text

    hello Alice
    hello Bob
    hello Charmaine
    bonjour Bob
    bonjour Alice
    bonjour Charmaine

Complex specifications
~~~~~~~~~~~~~~~~~~~~~~

In the above examples we are using the try everything approach, however there is more control over
how variables are specified. By default we are using a product iterator, which could be explicitly
defined like so

.. code:: yaml

    command: echo {greeting} {name}
    variables:
        product:
            greeting:
                - hello
                - bonjour
            name:
                - Alice
                - Bob
                - Charmaine

however if we know that Alice speaks English, Bob speaks French, and Charmaine speaks Spanish we can
use a similar specification, however instead of a product iterator we can use zip.

.. code:: yaml

    command: echo {greeting} {name}
    variables:
        zip:
            greeting:
                - hello
                - bonjour
                - hola
            name:
                - Alice
                - Bob
                - Charmaine

This is just the python ``zip`` function under the hood, and will produce the output

.. code:: text

    hello Alice
    bonjour Bob
    hola Charmaine

This definition of the iterator applies to all variables defined in the level directly under the
iterator. So if we wanted to ``echo`` to the screen and assuming we are on macOS use the ``say``
command,

.. code:: yaml

    command: {command} {greeting} {name}
    variables:
        command:
            - echo
            - say
        zip:
            greeting:
                - hello
                - bonjour
                - holj
            name:
                - Alice
                - Bob
                - Charmaine

In the above specification, we are applying the ``zip`` iterator to the variables greeting and name,
however all the resulting values will then use the ``product`` iterator, resulting in the following
sequence of commands.

.. code:: text

    echo hello Alice
    echo bonjour Bob
    echo hola Charmaine
    say hello Alice
    say bonjour Bob
    say hola Charmaine

In more complicated contexts multiple ``zip`` iterators are supported by having each set of values
nested in a list.

.. code:: yaml

    variables:
        zip:
            - var1: [1, 2, 3]
              var2: [4, 5, 6]
            - var3: ['A', 'B', 'C']
              var4: ['D', 'E', 'F']

Which will ``zip`` ``var1`` and ``var2``, separately zip ``var3`` and ``var4``, then take the
product of the result of those two operations.

Range Specification
~~~~~~~~~~~~~~~~~~~

In cases where the number of values for a variable are too numerous to list
manually, Experi supports a range operator, specified using ``!arange`` like below

.. code:: yaml

    var: !arange 100

``!arange`` reflects the use of the NumPy ``arange`` function to generate the values.
Like the NumPy function this also has arguments for the ``start``, ``stop``, ``step``
and ``dtype`` which can all be specified as key value pairs

.. code:: yaml

    var: !arange
        start: 100
        stop: 110
        step: 2.5
        dtype: float

which will set ``var`` to ``[100., 102.5 105., 107.5]``. In this case this specification
is not particularly helpful, however, for hundreds of values

.. code:: yaml

    var: !arange
        stop: 500
        step: 5

this approach is a definite improvement.

pbs
---

This section is for the specification of the options for submission to a job scheduler.

The simplest case is just specifying

.. code:: yaml

    pbs: True

which will submit the job to the scheduler using the default values which are

.. code:: yaml

    pbs:
        ncpus: 1
        select: 1
        walltime: 1:00
        setup: ''

Of these default values ``setup`` is the only one that should require explaining. This is a sequence
of commands in the pbs file that setup the environment, like loading modules, modifying the PATH,
activating a virtual end, etc. They are just inserted at the top of the file before the command is
run.

.. code:: yaml

    pbs:
        setup:
            - module load hoomd
            - export PATH=$HOME/.local/bin:$PATH

While there are some niceties to make specifying options easier it is possible to pass any option by
using the flag as the dictionary key like in the example below with the mail address ``M`` and path
to the output stream ``o``

.. code:: yaml

    pbs:
        M: malramsay64@gmail.com
        o: dest

.. _YAML Guide: intro_to_yaml
.. _Wikipedia:
.. _YAML: https://en.wikipedia.org/wiki/YAML
.. _Ansible YAML Reference: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
.. _YAML Lint: http://www.yamllint.com/
.. _yaml.org: http://yaml.org/
.. _python string formatting documentation: https://docs.python.org/3/library/string.html#format-string-syntax
.. _pyformat.info: https://pyformat.info/
.. _experi #12: https://github.com/malramsay64/experi/issues/12
