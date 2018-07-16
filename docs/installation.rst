Installation
============

Experi is compatible with python>==3.6 supporting installation using ``pip``

.. code-block:: shell

    pip3 install experi

Note that for the command ``experi`` to work the directory containing the executable needs to be in
the ``PATH`` variable. In most cases this will probably be ``$HOME/.local/bin`` although this is
installation dependent. If you don't know where the executable is, on \*nix systems the command

.. code-block:: shell

    find $HOME -name experi

will search everywhere in your home directory to find it. Alternatively replacing ``$HOME`` with
``/`` will search everywhere.

For installation from source

.. code-block:: shell

    git clone https://github.com/malramsay64/experi.git
    cd experi
    pip3 install .

Install of the development environment requires ``pipenv``, which has comprehensive `install
instuctions <https://docs.pipenv.org/install/#installing-pipenv>`_ avalable. Once ``pipenv`` is
installed, you can install the development dependencies with the command

.. code-block:: shell

    pipenv install --dev --three

which creates a virtual environment for the project into which the exact versions of all requried
packages is installed. You can activaete the  virtualenv by running

.. code-block:: shell

    pipenv shell

which creates a new shell with the environment activated. Alternatively, a single command (like the
test cases) can be run using

.. code-block:: shell

    pipenv run pytest

For those of you trying to run this on a cluster with only user privileges including the ``--user``
flag will resolve issues with pip requiring elevated permissions installing to your home directory
rather than for everyone.

.. code-block:: shell

    pip3 install --user experi
