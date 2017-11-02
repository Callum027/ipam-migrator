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
import json


class Database(object):
    '''
    Database object type.
    '''


    def __init__(self,
                 name,
                 ip_addresses=None,
                 prefixes=None,
                 vlans=None,
                 vrfs=None):
        '''
        Database object constructor.
        '''

        self.name = name

        self.ip_addresses = copy.deepcopy(ip_addresses) if ip_addresses is not None else dict()
        self.prefixes = copy.deepcopy(prefixes) if prefixes is not None else dict()
        self.vlans = copy.deepcopy(vlans) if vlans is not None else dict()
        self.vrfs = copy.deepcopy(vrfs) if vrfs is not None else dict()


    def __str__(self):
        '''
        Human-readable stringifier method for databases,
        suitable for dumping to output.
        '''

        return json.dumps(
            {
                "name": self.name,
                "ip_addresses": [ip.as_dict() for ip in self.ip_addresses.values()],
                "prefixes": [prefix.as_dict() for prefix in self.prefixes.values()],
                "vlans": [vlans.as_dict() for vlans in self.vlans.values()],
                "vrfs": [vrf.as_dict() for vrf in self.vrfs.values()],
            },
        )
