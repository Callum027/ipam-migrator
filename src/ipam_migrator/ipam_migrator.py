#
# IPAM database migration script
# ipam_migrator/ipam_migrator.py - main routine
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


'''
Main routine.
'''


import argparse


def main():
    '''
    Main routine.
    '''

    # Parse
    argparser = argparse.ArgumentParser(
        description="Transfer IPAM information between two (possibly differing) systems",
    )

    argparser.add_argument(
        "-l", "--log",
        metavar="FILE",
        type=str,
        default=None,
        help="log output to FILE",
    )

    argparser.add_argument(
        "-ll", "--log-level",
        metavar="LEVEL",
        type=str,
        default=None,
        help="use LEVEL as the logging level parameter",
    )

    argparser.add_argument(
        "input_api_data",
        metavar="INPUT-API-ENDPOINT,TYPE,TOKEN|(USER,PASSWORD)",
        type=str,
        help="input database API endpoint, type, and token or user-password pair",
    )

    argparser.add_argument(
        "output_api_data",
        metavar="OUTPUT-API-ENDPOINT,TYPE,TOKEN|(USER,PASSWORD)",
        type=str,
        default=None,
        help="output database API endpoint, type, and token or user-password pair",
    )

    args = vars(argparser.parse_args())

    #
    input_api_data = args["input_api_data"].split(",")
    input_api_endpoint = input_api_data[0]
    input_api_type = input_api_data[1]
    if len(input_api_data) == 3:
        input_api_token = input_api_data[2]
        input_api_user = None
        input_api_password = None
    else:
        input_api_token = None
        input_api_user = input_api_data[2]
        input_api_password = input_api_data[3]

    if "output_api_data" in args:
        output_api_data = args["output_api_data"].split(",")
        output_api_endpoint = output_api_data[0]
        output_api_type = output_api_data[1]
        if len(output_api_data) == 3:
            output_api_token = output_api_data[2]
            output_api_user = None
            output_api_password = None
        else:
            output_api_token = None
            output_api_user = output_api_data[2]
            output_api_password = output_api_data[3]

    # Set up the logger.

    # Connect to the input API endpoint, and read its database.
    if input_api_type == "phpipam":
        input_backend = PhpIPAM(input_api_endpoint, input_api_user, input_api_password)
    elif input_api_type == "netbox":
        input_backend = NetBox(input_api_endpoint, input_api_token)
    else:
        raise RuntimeError("unknown input database backend type '{}'".format(input_api_type))

    input_database = input_backend.database_read()

    # If an output database is specified, connect to the output API endpoint,
    # and write the input database to it.
    if "output_api_data" in args:
        if output_api_type == "phpipam":
            output_backend = PhpIPAM(output_api_endpoint, output_api_user, output_api_password)
        elif output_api_type == "netbox":
            output_backend = NetBox(output_api_endpoint, output_api_token)
        else:
            raise RuntimeError("unknown output database backend type '{}'".format(output_api_type))

        output_backend.database_write(input_database)

    # If not, write the input database to output.
    else:
        logger.info("Input database:\n{}".format(input_database))
        
