#
# IPAM database migration script
# ipam_migrator/db/database.py - database object type
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
Database object type.
'''


import copy


class Database(object):
    '''
    Database object type.
    '''


    def __init__(self,
                 name,
                 roles=None,
                 services=None,
                 ip_addresses=None,
                 prefixes=None,
                 aggregates=None,
                 vlans=None,
                 vlan_groups=None,
                 vrfs=None):
        '''
        Database object constructor.
        '''

        self.name = name

        self.roles = copy.deepcopy(roles)
        self.services = copy.deepcopy(services)
        self.ip_addresses = copy.deepcopy(ip_addresses)
        self.prefixes = copy.deepcopy(prefixes)
        self.aggregates = copy.deepcopy(aggregates)
        self.vlans = copy.deepcopy(vlans)
        self.vlan_groups = copy.deepcopy(vlan_groups)
        self.vrfs = copy.deepcopy(vrfs)


    def __str__(self):
        '''
        Human-readable stringifier method for databases,
        suitable for dumping to output.
        '''

        return "reached the end"
