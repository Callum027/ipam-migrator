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

# A helper program to take in a list of key-value pairs, process
# an input file with respect to this list, and then write the result
# to the given output location.


import argparse
import re


def template_process(config, input_file, output_file):
    '''
    Process the given input file with respect to the given config,
    and write the result to the output file.
    '''

    with open(input_file, "r", encoding="UTF-8") as i:
        with open(output_file, "w", encoding="UTF-8") as o:
            text = i.read()

            for key, value in config.items():
                text = re.sub("__%s__" % key, value, text)

            o.write(text)


# Get arguments.
argparser = argparse.ArgumentParser()

argparser.add_argument(
    "input-file",
    metavar = "INFILE",
    type = str,
    help ="template file to process",
)

argparser.add_argument(
    "output-file",
    metavar = "OUTFILE",
    type = str,
    help ="location to save processed file to",
)

argparser.add_argument(
    "config",
    metavar = "KEY=VALUE",
    type = str,
    nargs = "*",
    help ="key-value pair to replace in the template",
)

args = vars(argparser.parse_args())


# Process configuration from arguments.
input_file = args["input-file"]
output_file = args["output-file"]

config = {}

for string in args["config"]:
    k, value = string.split("=", maxsplit=1)
    key = k.upper().replace("-", "_")

    config[key] = value


# Process the template.
template_process(config, input_file, output_file)
