#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""
"""

from setuptools import find_packages, setup

setup(
    name='experirun',
    version='0.0.1',
    python_requires='>=3.6',
    setup_requires=[],
    install_requires=[],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        experirun=experirun.run:main
    """,
    url='',
    author='Malcolm Ramsay',
    author_email='malramsay64@gmail.com',
    description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
