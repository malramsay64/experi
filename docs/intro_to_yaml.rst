Introduction to YAML
====================

Experi uses the `YAML`_ file format for the input file since it has widespread use and support and
the format is simple for a human to parse. From the perspective of a python developer, YAML is a
method of specifying python data structures in a text file. A key construct of the YAML file is the
mapping of a *key* to a *value*, like a python dictionary. Also like a python dictionary the
mapping uses the colon

.. code:: yaml

   key: value

All *keys* have to be strings, although *values* can be a range of types. Values that look like a
string, will become python strings, values that are integers will become python integers, and
values that are floats will become python floats. A value can also be itself a mapping

.. code:: yaml

   key:
     value1: 1
     value2: 2
     value3: 3
     value4: 4

where the above example is the same as the python data structure

.. code:: python

   {'"key"': {"value1": 1, "value2": 2, "value3": 3, "value4": 4}}

YAML also supports using lists as values, which are denoted with bullet points

.. code:: yaml

   key:
     - 1
     - 2
     - 3
     - 4

where the value is now the python list ``[1, 2, 3, 4]``. The python list syntax is another way to
specify a list in a YAML file with the example below having the same value as the example above

.. code:: yaml

   key: [1, 2, 3 4]


The final feature of YAML files I will highlight here is the specification of long strings, which
are particularly useful when writing long bash commands. To create a long *single* line string,
start the string with the ``>`` character.

.. code:: yaml

   key: >
     A long string
     written over
     multiple lines


which will have no newline characters inserted. This is so much better than having to end line in
bash with a ``\``. To include the newlines in the string, you can instead use the ``|`` symbol

.. code:: yaml

   key: |
     Line 1
     Line 2
     Line 3
     END

which includes a newline character after each number.

The examples presented should be enough to get started using Experi. The following resources are
recommended for further reading

- `Ansible YAML Reference`_
- `Wikipedia`_
- `YAML Lint`_
- `yaml.org`_
