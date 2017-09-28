#
# IPAM database migration script
# ipam_migrator/db/ip/prefix.py - Internet Protocol (IP) subnet prefixes
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
Internet Protocol (IP) subnet prefixes.
'''


import ipaddress

from ipam_migrator.db.object import Object


class Prefix(Object):
    '''
    Database type for Internet Protocol (IP) subnet prefixes.
    '''


    def __init__(self,
                 prefix_id,
                 prefix,
                 is_pool=False,
                 name=None, description=None,
                 role_id=None, status_id=None,
                 vlan_id=None, vrf_id=None):
        '''
        VLAN object constructor.
        '''

        super().__init__(prefix_id, name, description)

        self.prefix = ipaddress.ip_network(prefix)
        self.family = 6 if isinstance(self.prefix, ipaddress.IPv6Network) else 4

        self.is_pool = is_pool

        self.role_id = role_id
        self.status_id = status_id

        self.vlan_id = vlan_id
        self.vrf_id = vrf_id


    def __str__(self):
        '''
        Human-readable stringifier method for Internet Protocol (IP) subnet prefixes,
        suitable for dumping to output.
        '''

        return self.object_str(
            prefix=self.prefix,
            family=self.family,

            is_pool=self.is_pool,

            role_id=self.role_id,
            status_id=self.status_id,

            vlan_id=self.vlan_id,
            vrf_id=self.vrf_id,
        )
