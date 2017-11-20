#
# IPAM database migration script
# ipam_migrator/backend/base.py - database backend base class
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
Database backend base class.
'''


import abc


class BaseBackend(abc.ABC):
    '''
    Database backend base class.
    '''


    def __init__(self, logger, dry_run, name):
        '''
        Database backend constructor.
        '''

        self.logger = logger
        self.dry_run = dry_run
        self.name = name


    @abc.abstractmethod
    def database_read(self,
                      read_ip_addresses=True,
                      read_prefixes=True,
                      read_vlans=True,
                      read_vrfs=True):
        '''
        Read a Database object from this backend.
        '''

        pass


    @abc.abstractmethod
    def database_write(self, database):
        '''
        Write a Database object to this backend.
        '''

        pass
