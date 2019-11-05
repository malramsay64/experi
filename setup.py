#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

from setuptools import find_packages, setup


# Get the version from src/experi/version.py without importing the package
def get_version():
    g = {}
    exec(open("src/experi/version.py").read(), g)
    return g["__version__"]


with open("README.md") as f:
    long_description = f.read()

install_require = ["click", "pyyaml>=5.0", "numpy"]
dev_require = [
    "mypy==0.740",
    "pylint==2.4.3",
    "pytest==5.2.2",
    "black==19.10b0",
    "coverage==4.5.4",
    "pytest-cov==2.8.1",
    "hypothesis>=4.42.0,<5.0",
    "attrs>=19.2",
]
docs_require = ["sphinx", "sphinx-autobuild", "sphinx-rtd-theme", "sphinx-click"]

setup(
    name="experi",
    version=get_version(),
    python_requires=">=3.6",
    setup_requires=[],
    install_requires=install_require,
    extras_require={"dev": dev_require, "docs": docs_require},
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        experi=experi.run:main
    """,
    url="https://github.com/malramsay64/experi",
    author="Malcolm Ramsay",
    author_email="malramsay64@gmail.com",
    description="An interface for managing computational experiments with many independent variables.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
