#!/usr/bin/env python3
#
# Copyright (c) 2017 Catalyst.net Ltd
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# A setuptools based setup module.
# See:
# https://packaging.python.org/en/latest/distributing.html
# https://github.com/pypa/sampleproject


import os
import setuptools
import stat
import sys
import re


# Top-level source directory.
here = os.path.abspath(os.path.dirname(__file__))


# Get the long description from the README file.
with open(os.path.join(here, "README.md"), "r", encoding="UTF-8") as f:
    long_description = f.read()


# Setup the package.
setuptools.setup(
    name = "l3overlay",

    description = "IPsec overlay network manager",
    long_description = long_description,

    version = "1.0.0",

    url = "https://github.com/catalyst/l3overlay",

    author = "Callum Dickinson",
    author_email = "callum.dickinson@catalyst.net.nz",

    license = "GPLv3+",

    classifiers = [
        "Development Status :: 5 - Production/Stable",

        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",

        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",

        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],

    keywords = "l3overlay ipsec bird routing namespace mesh network",

    install_requires = ["jinja2", "pyroute2>=0.4.6"],

    packages = setuptools.find_packages(where=os.path.join(here, "src")),
    package_dir = {"": "src"},

    entry_points = {
        "console_scripts": [
            "l3overlayd = l3overlay.l3overlayd.main:main",
            "l3overlay-birdc = l3overlay.l3overlay_birdc:main",
        ],
    },

    package_data = {
        'l3overlay': [
            os.path.join("template", "bird.conf"),
            os.path.join("template", "ipsec.conf"),
            os.path.join("template", "ipsec.secrets"),
        ],
    },
)
