#
# Migrator tool for phpIPAM-NetBox
# migrator/db/__init__.py - Database object
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
Database object.
'''


import copy
import ipaddress
import json


class Database(object):
    '''
    Database object.
    '''


    # pylint: disable=too-few-public-methods


    # pylint: disable=too-many-arguments
    def __init__(self,
                 roles,
                 ip_addresses, prefixes, aggregates,
                 vlans, vlan_groups,
                 vrfs):
        '''
        Database object constructor.
        '''

        self.roles = tuple(copy.deepcopy(roles))

        self.ip_addresses = tuple(copy.deepcopy(ip_addresses))
        self.prefixes = tuple(copy.deepcopy(prefixes))
        self.aggregates = tuple(copy.deepcopy(aggregates))

        self.vlans = tuple(copy.deepcopy(vlans))
        self.vlan_groups = tuple(copy.deepcopy(vlan_groups))

        self.vrfs = tuple(copy.deepcopy(vrfs))


    def __str__(self):
        return json.dumps({
            "roles": self.roles,

            "ip_addresses": self.ip_addresses,
            "prefixes": self.prefixes,
            "aggregates": self.aggregates,

            "vlans": self.vlans,
            "vlan_groups": self.vlan_groups,

            "vrfs": self.vrfs,
        }, sort_keys=True, indent=4)
