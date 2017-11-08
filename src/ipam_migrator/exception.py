#
# IPAM database migration script
# ipam_migrator/exception.py - exception base class and implementations
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
Exception base class and implementations.
'''


class IpamMigratorError(Exception):
    '''
    IPAM migrator exception base class.
    '''

    pass


class AuthDataNotFoundError(IpamMigratorError):
    '''
    Exception for required auth data not being found.
    '''

    def __init__(self, name, api_type, param_description):
        '''
        AuthDataNotFoundError initialisation method.
        '''

        super().__init__(
            "{} database backend type '{}' expects auth data parameter(s) {}, none found".format(
                name,
                api_type,
                param_description,
            ),
        )


class AuthMethodUnsupportedError(IpamMigratorError):
    '''
    Exception for the given auth method being unsupported.
    '''

    def __init__(self, api_type, api_auth_method, supported_methods):
        '''
        AuthMethodUnsupportedError initialisation method.
        '''

        if len(supported_methods) == 1:
            supported_methods_formatted = "'{}'".format(supported_methods[0])
        elif len(supported_methods) > 1:
            supported_methods_quoted = ["'{}'".format(met) for met in supported_methods]
            supported_methods_formatted = ", ".join(supported_methods_quoted[0:-1])
            supported_methods_formatted += " or {}".format(supported_methods_quoted[-1])

        super().__init__(
            "authentication method '{}' unsupported by database backend type '{}', "
            "please use {} instead".format(
                api_auth_method,
                api_type,
                supported_methods_formatted,
            ),
        )


class APIGetError(IpamMigratorError):
    '''
    Exception for API GET method error.
    '''

    def __init__(self, code, message):
        '''
        APIGetError initialisation method.
        '''

        self.api_code = code
        self.api_message = message
        super().__init__("ERROR {}: {}".format(self.api_code, self.api_message))


class APIOptionsError(IpamMigratorError):
    '''
    Exception for API OPTIONS method error.
    '''

    def __init__(self, code, message):
        '''
        APIOptionsError initialisation method.
        '''

        self.api_code = code
        self.api_message = message
        super().__init__("ERROR {}: {}".format(self.api_code, self.api_message))


class APIReadError(IpamMigratorError):
    '''
    Exception for API general read method error.
    '''

    def __init__(self, code, message):
        '''
        APIReadError initialisation method.
        '''

        self.api_code = code
        self.api_message = message
        super().__init__("ERROR {}: {}".format(self.api_code, self.api_message))


class APIWriteError(IpamMigratorError):
    '''
    Exception for API general write method error.
    '''

    def __init__(self, code, message):
        '''
        APIWriteError initialisation method.
        '''

        self.api_code = code
        self.api_message = message
        super().__init__("ERROR {}: {}".format(self.api_code, self.api_message))
