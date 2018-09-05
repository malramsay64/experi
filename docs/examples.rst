Examples
========

This is a collection of example workflows using Experi demonstrating some different ways of using it
for real experiments.

.. contents::
    :local:

Command Line Options
--------------------

This is an example of using Experi in my own research which was the reason I developed it. I have a
tool ``sdrun`` which translates command line options into a molecular dynamics simulation. This
experiment is investigating how temperature affects the motion of particles in the simulation. The
experiment consists of three separate parts;

1. The creation of a high temperature configuration which is well mixed (create)
2. Cooling the high temperature configuration to each of the desired temperatures for data
   collection (equil)
3. Collect data on the motion of particles within the simulation (prod)

The terms create, equil, and prod are the arguments to ``sdrun`` which reflect these stages. For
this simulation I would like each of the steps to be a separate job on the scheduler, hence I use
the ``jobs`` key. Part of the reason for this is that I am only creating a single configuration
for the step which is then used for each temperature in the equal step. By running as separate jobs
I will have a job with a single task for the first step which once finished will allow the
equilibration array job with 10 elements start.

.. code:: yaml

    # experiment.yml
    jobs:
      - command: >
         mpirun -np 12
         sdrun
         --pressure {pressure}
         --init-temp {init_temp}
         --temperature {create_temp}
         --lattice-lengths {cell_dims}
         --output {output}
         --steps {create_steps}
         create
         Trimer-P{pressure:.2f}-T{create_temp:.2f}.gsd

      - command: >
         mpirun -np 12
         sdrun
         --pressure {pressure}
         --init-temp {create_temp}
         --temperature {temperature}
         --output {output}
         --steps {equil_steps}
         equil
         Trimer-P{pressure:.2f}-T{create_temp:.2f}.gsd
         Trimer-P{pressure:.2f}-T{temperature:.2f}.gsd

      - command: >
         mpirun -np 12
         sdrun
         --pressure {pressure}
         --temperature {temperature}
         --output {output}
         --steps {steps}
         prod
         Trimer-P{pressure:.2f}-T{temperature:.2f}.gsd

    variables:
      create_temp: 0.80
      create_steps: 10_000_000
      equil_steps: 100_000_000
      output: output
      steps: 200_000_000
      pressure: 1.00
      temperature:
        - 0.30
        - 0.32
        - 0.34
        - 0.36
        - 0.38
        - 0.40
        - 0.42
        - 0.44
        - 0.46
        - 0.50

    pbs:
      setup:
        - export PATH="$HOME/.pyenv/versions/crystal/bin:$PATH"
      cpus: 12
      memory: 16gb
      walltime: 100:00:00
      project: PRJ-CrysGrowth
      o: logs
      j: oe

Input Files
-----------

A common workflow for many software packages is to define the workflow with the use of input
files. Better support for input files is planned (see `issue <experi #>`), though it is still
possible to use them. The below example creates an input file for using with the software LAMMPS.


.. code:: yaml

   # experiment.yml

   command:
     - |
       echo -e "
       <file>
       " < file.in
     - lmp_run -in file.in

Subdirectories
--------------

Breaking the output into a subdirectories allows for more organisation of experimental result,
particularly where there are many output files generated. Experi will always run from the
directory containing the experiment.yml file, however that doesn't prevent you from creating
subdirectories and running commands in them. This example shows how you can use Experi to run code
in a separate subdirectory for each set of variables.

.. code:: yaml

    command:
      - mkdir -p <direcotry>
      - cd <directory>
      - run command
