#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test the command line interface to experirun."""

import subprocess


def test_command():
    proc_out = subprocess.check_output(['experi'], cwd='test/data')
    with open('test/data/result.txt', 'rb') as source:
        expected = source.read()
    assert proc_out == expected
