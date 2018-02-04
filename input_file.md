experiment.yml
==============

This document is a guide to the `experiment.yml` file
which is used as the input file for experi.
All the parameters for simulation should be specified in this folder.
The `experiment.yml` file is designed to be located
in the same directory as the results,
so there is no simple method for specifying
another directory as the working directory.

The `experiment.yml` file is broken into a number of sections
which each have their own roles and behaviour.
These sections are listed below;
- [name](#name)
- [command](#command)
- [variables](#variables)
- [pbs](#pbs)

name
----

This is the name of the project or simulation.
Currently the only functionality this provides is
an optional method of specifying the job name for pbs scripts.

```yaml
# experiment.yml

name: test experiment
```

command
--------

This is where the sequence of commands for the experiment are specified.
Here bash commands are specified as a string,
with variables notated with curly braces as below
```yaml
# experiment.yml

command: echo {variable1}
```
Here `{variable1}` is replaced with the contents of `variable1`
as specified in the variables section of the file.
The variables are filled using python string formatting,
allowing for more complicated definitions of formatting where required.
Any number of variables can be added to the command,
with duplication of variables being perfectly reasonable.
The restrictions to the specification of variables is that they are not `value` or `iterator`,
since these are reserved for the parsing of the values of the variables,
and any of the restrictions on python variables.

Along with supporting a single command,
multiple commands can be specified as a list
```yaml
# experiment.yml

command:
    - echo {variable1}
    - echo {variable1} {variable2}
```
Here all the instances of the first command run,
then all of the second command.

In the above example,
where there are more variables in one command than another,
experi will ensure that commands are unique before running them.
Even though there might be a list of values for variable2,
only the distinct values for variable1 will be run in the first command.


variables
---------

This is where the real power of experi lies,
in being able to specify complex sets of variables
in a simple human readable fashion.
Variables are specified using the names
as given in the command section.
The simplest case is for a single value of a variable
```yaml
# experiment.yml

command: echo hello {name}

variables:
    name:
        value: Alice
```
with the value being specified using the `value` key.
For simple applications this `value` key can be discarded
giving the simpler form
```
variables:
    variable1: Alice
```

Specifying lists of variables can be done in the same way as the commands,
again for this simple case, the `value` keyword is optional
```
variables:
    variable1:
        value:
            - Alice
            - Bob
            - Charmaine
```

### Multiple Variables

Specifying multiple variables is as simple as specifying a single variable,
however by default, all possible combinations of the variables are generated.
In the simplest case,
with just a single value per variable
```
command: echo {greeting} {name}
variables:
    greeting: hello
    name: Alice
```
the resulting of the command would be `hello Alice`.
To greet multiple people we just add more names
```
comamnd: echo {greeting} {name}
variables:
    greeting: hello
    name:
        - Alice
        - Bob
        - Charmaine
```
which would result in
```
hello Alice
hello Bob
hello Charmaine
```
We have all possible combinations of the greeting and the name.
Extending this, to greet all the people in both English and French
we can add both the greetings, and all the names giving the input file
```
command: echo {greeting} {name}
variables:
    greeting: 
        - hello
        - bonjour
    name:
        - Alice
        - Bob
        - Charmaine
```
and resulting in the output
```
hello Alice
hello Bob
hello Charmaine
bonjour Bob
bonjour Alice
bonjour Charmaine
```

### Complex specifications

In the above examples we are using the try everything approach,
however there is more control over how variables are specified.
By default we are using a product iterator,
which could be explicitly defined like so
```
command: echo {greeting} {name}
variables:
    greeting: 
        - hello
        - bonjour
    name:
        - Alice
        - Bob
        - Charmaine
    iterator: product
```
however if we know that 
Alice speaks English,
Bob speaks French, and 
Charmaine speaks Spanish
we can use a similar specification,
however instead of a product iterator we can use zip.
```
command: echo {greeting} {name}
variables:
    greeting: 
        - hello
        - bonjour
        - hola
    name:
        - Alice
        - Bob
        - Charmaine
    iterator: zip
```
This is just the python `zip` function under the hood,
and will produce the output
```
hello Alice
bonjour Bob
hola Charmaine
```
This definition of the iterator applies to
all variables at the same level as the iterator definition.
So if we wanted to `echo` to the screen 
and assuming we are on macOS use the `say` command,
we need to make use of the `value` keyword.
```
command: {command} {greeting} {name}
variables:
    command:
        - echo
        - say
    greeting:
        value:
            - hello
            - bonjour
            - hola
        name:
            - Alice
            - Bob
            - Charmaine
        iterator: zip
```
In the above specification,
we are applying the `zip` iterator to the variables specified under greeting,
however all the resulting values will then use the `product` iterator,
resulting in the following sequence of commands.
```
echo hello Alice
echo bonjour Bob
echo hola Charmaine
say hello Alice
say bonjour Bob
say hola Charmaine
```

pbs
---

This section is for the specification of the options for submission to a job scheduler.
Currently, the submission only works on quartz,
a machine in the Chemistry department at the University of Sydney,
however I do plan to make it more configurable.

The simplest case is just specifying
```
pbs: True
```
which will submit the job to the scheduler using the default values
which are
```
pbs:
    cpus: 1
    nodes: 1
    walltime: 1:00
    setup: ''
```
Of these default values `setup` is the only one that should require explaining.
This is a sequence of commands in the pbs file that setup the environment,
like loading modules, modifying the PATH, activating a virtualenv, etc.
They are just inserted at the top of the file before the command is run.
```
pbs:
    setup:
        - module load hoomd
        - export PATH=$HOME/.local/bin:$PATH
```

### Multiple Commands and Variables

The key reason I wrote experi was to generate scripts for pbs array jobs.
So when many variables are specified,
a pbs file is generated containing all the combinations of variables,
which is run as an array job.
A file is generated in the working directory,
allowing for the file to be inspected.

Where there is a list of commands,
each command has it's own file with the set of variable combinations.
These are submitted to run sequentially using the `-W depends=afterok`
option in the job submission.
