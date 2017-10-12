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
import logging
import os
import stat

from ipam_migrator.backend.netbox import NetBox
from ipam_migrator.backend.phpipam import PhpIPAM

from ipam_migrator.exception import AuthDataNotFoundError


def main():
    '''
    Main routine.
    '''

    # Parse
    argparser = argparse.ArgumentParser(
        description="Transfer IPAM information between two (possibly differing) systems",
    )

    argparser.add_argument(
        "input_api_data",
        metavar="INPUT-API-ENDPOINT,TYPE,AUTH-METHOD,KEY|TOKEN|(USER,PASSWORD)",
        type=str,
        help="input database API endpoint, type, authentication method and required information",
    )

    argparser.add_argument(
        "output_api_data",
        metavar="OUTPUT-API-ENDPOINT,TYPE,AUTH-METHOD,KEY|TOKEN|(USER,PASSWORD)",
        type=str,
        nargs="?",
        default=None,
        help="output database API endpoint, type, authentication method and required information",
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
        default="INFO",
        help="use LEVEL as the logging level parameter",
    )

    arg_input_ssl_verify = argparser.add_mutually_exclusive_group(required=False)
    arg_input_ssl_verify.add_argument(
        "-iasv", "--input-api-ssl-verify",
        action="store_true",
        help="verify the input API endpoint SSL certificate (default)",
    )
    arg_input_ssl_verify.add_argument(
        "-naisv", "--no-input-api-ssl-verify",
        action="store_false",
        help="do NOT verify the input API endpoint SSL certificate",
    )

    arg_output_ssl_verify = argparser.add_mutually_exclusive_group(required=False)
    arg_output_ssl_verify.add_argument(
        "-oasv", "--output-api-ssl-verify",
        action="store_true",
        help="verify the output API endpoint SSL certificate (default)",
    )
    arg_output_ssl_verify.add_argument(
        "-noasv", "--no-output-api-ssl-verify",
        action="store_false",
        help="do NOT verify the output API endpoint SSL certificate",
    )

    args = vars(argparser.parse_args())

    # Set up the logger.
    log = args["log"]
    log_level = args["log_level"]

    logger = logging.getLogger("ipam-migrator")
    logger.setLevel(log_level)

    logger_formatter = logging.Formatter("%(asctime)s %(name)s: [%(levelname)s] %(message)s")

    logger_streamhandler = logging.StreamHandler()
    logger_streamhandler.setFormatter(logger_formatter)
    logger.addHandler(logger_streamhandler)

    if log:
        os.makedirs(os.path.dirname(log), exist_ok=True)
        logger_filehandler = logging.FileHandler(log)
        logger_filehandler.setFormatter(logger_formatter)
        os.chmod(log, stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IROTH)
        logger.addHandler(logger_filehandler)

    logger.debug("started logger")

    # Start main routine, with exception capture for logging purposes.
    try:
        #
        input_api_data = api_data_read(logger, args, "input")
        input_api_endpoint = input_api_data[0]
        input_api_type = input_api_data[1]
        input_api_auth_method = input_api_data[2]
        input_api_auth_data = input_api_data[3]
        input_api_ssl_verify = input_api_data[4]

        if args["output_api_data"]:
            use_output = True
            output_api_data = api_data_read(logger, args, "output")
            output_api_endpoint = output_api_data[0]
            output_api_type = output_api_data[1]
            output_api_auth_method = output_api_data[2]
            output_api_auth_data = output_api_data[3]
            output_api_ssl_verify = output_api_data[4]
        else:
            use_output = False

        # Configuration verification.
        api_data_check(
            logger, "input",
            input_api_endpoint, input_api_type,
            input_api_auth_method, input_api_auth_data,
            input_api_ssl_verify,
        )

        if use_output:
            api_data_check(
                logger, "output",
                output_api_endpoint, output_api_type,
                output_api_auth_method, output_api_auth_data,
                output_api_ssl_verify,
            )

        # Connect to the input API endpoint, and read its database.
        input_backend = backend_create(
            logger, "input",
            input_api_endpoint, input_api_type,
            input_api_auth_method, input_api_auth_data,
            input_api_ssl_verify,
        )
        input_database = input_backend.database_read()

        # If an output database is specified, connect to the output API endpoint,
        # and write the input database to it.
        if use_output:
            output_backend = backend_create(
                logger, "output",
                output_api_endpoint, output_api_type,
                output_api_auth_method, output_api_auth_data,
                output_api_ssl_verify,
            )
            output_backend.database_write(input_database)

        # If not, write the input database to the logger.
        else:
            logger.info("Input database:\n{}".format(input_database))

    except Exception as e:
        logger.exception(e)

    # Main routine shutdown.
    logger.debug("stopping logger")
    logger.removeHandler(logger_streamhandler)
    if log:
        logger.removeHandler(logger_filehandler)


def api_data_read(logger, args, name):
    '''
    '''

    api_data_list = args["{}_api_data".format(name)].split(",")
    api_endpoint = api_data_list[0]
    api_type = api_data_list[1]
    api_auth_method = api_data_list[2]
    api_auth_data = api_data_list[3:]
    if args["{}_api_ssl_verify".format(name)] is False and \
       args["no_{}_api_ssl_verify".format(name)] is True:
        api_ssl_verify = True # Default case
    else:
        api_ssl_verify = args["{}_api_ssl_verify".format(name)]

    return (api_endpoint, api_type, api_auth_method, api_auth_data, api_ssl_verify)


def api_data_check(logger,
                   name,
                   api_endpoint, api_type,
                   api_auth_method, api_auth_data,
                   api_ssl_verify):
    '''
    '''

    if api_auth_method == "key":
        if not api_auth_data:
            raise AuthDataNotFoundError(name, api_type, "API key")
    elif api_auth_method == "token":
        if not api_auth_data:
            raise AuthDataNotFoundError(name, api_type, "authentication token")
    elif api_auth_method == "login":
        if not api_auth_data:
            raise AuthDataNotFoundError(name, api_type, "user name and password")
        if len(api_auth_data) < 2:
            raise AuthDataNotFoundError(name, api_type, "password")


def backend_create(logger,
                   name,
                   api_endpoint, api_type,
                   api_auth_method, api_auth_data,
                   api_ssl_verify):
    '''
    '''

    if api_type == "phpipam":
        return PhpIPAM(logger, name, api_endpoint, api_auth_method, api_auth_data, api_ssl_verify)
    elif api_type == "netbox":
        return NetBox(logger, name, api_endpoint, api_auth_method, api_auth_data, api_ssl_verify)
    else:
        raise RuntimeError("unknown {} database backend type '{}'".format(name, api_type))
