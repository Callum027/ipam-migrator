#
# Migrator tool for phpIPAM-NetBox
# migrator/backend/base.py - migrator backend base class
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
Migrator backend base class.
'''


import abc


class BaseBackend(meta=abc.ABCMeta):
    '''
    Migrator backend base class.
    '''


    @abc.abstractmethod
    def database_read(self,
                      read_roles=True,
                      read_services=True,
                      read_ip_addresses=True,
                      read_prefixes=True,
                      read_aggregates=True,
                      read_vlans=True,
                      read_vlan_groups=True,
                      read_vrfs=True):
        '''
        '''

        pass


    @abc.abstractmethod
    def database_write(self, database):
        '''
        '''

        pass
