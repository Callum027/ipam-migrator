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


    # pylint: disable=too-many-arguments
    def __init__(self,
                 prefix_id,
                 prefix,
                 is_pool=False,
                 description=None,
                 vlan_id=None, vrf_id=None):
        '''
        VLAN object constructor.
        '''

        super().__init__(prefix_id, None, description)

        self.prefix = ipaddress.ip_network(prefix)
        self.family = 6 if isinstance(self.prefix, ipaddress.IPv6Network) else 4

        self.is_pool = bool(is_pool) if is_pool is not None else None

        self.vlan_id = int(vlan_id) if vlan_id is not None else None
        self.vrf_id = int(vrf_id) if vrf_id is not None else None


    def __str__(self):
        '''
        String representation of a Prefix.
        '''

        if self.description:
            return "prefix {} with description '{}'".format(self.prefix, self.description)
        return "prefix {}".format(self.prefix)


    def as_dict(self):
        '''
        Dictionary representation of a Prefix.
        '''

        return {
            "id": self.id_get(),
            "description": self.description,

            "prefix": str(self.prefix),
            "family": self.family,

            "is_pool": self.is_pool,

            "vlan_id": self.vlan_id,
            "vrf_id": self.vrf_id,
        }
