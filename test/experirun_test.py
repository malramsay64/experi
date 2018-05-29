#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the command line interface to experirun."""

import subprocess
from ruamel.yaml import YAML as yaml


def test_command():
    proc_out = subprocess.check_output(["experi"], cwd="test/data")
    with open("test/data/experiment.yml", "rb") as source:
        testfile = yaml().load(source)
    assert proc_out.decode() == testfile["result"]
