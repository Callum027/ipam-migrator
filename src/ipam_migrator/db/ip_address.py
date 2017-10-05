#
# IPAM database migration script
# ipam_migrator/db/ip/address.py - Internet Protocol (IP) addresses
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
Internet Protocol (IP) addresses.
'''


import ipaddress

from ipam_migrator.db.object import Object


class IPAddress(Object):
    '''
    Database type for Internet Protocol (IP) addresses.
    '''


    def __init__(self,
                 address_id,
                 address,
                 description=None,
                 custom_fields=None,
                 status_id=None, nat_inside_id=None, nat_outside_id=None,
                 vrf_id=None):
        '''
        VLAN object constructor.
        '''

        # Initialise database object with ID.
        super().__init__(address_id, None, description)

        # Internal fields.
        self.address = ipaddress.ip_address(address)
        self.family = 6 if isinstance(self.address, ipaddress.IPv6Address) else 4
        self.custom_fields = custom_fields.copy() if custom_fields is not None else dict()

        # External fields.
        self.status_id = int(status_id) if status_id is not None else None
        self.nat_inside_id = int(nat_inside_id) if nat_inside_id is not None else None
        self.nat_outside_id = int(nat_outside_id) if nat_outside_id is not None else None

        # Grouping fields, in ascending order of scale.
        self.vrf_id = int(vrf_id) if vrf_id is not None else None


    def as_dict(self):
        '''
        '''

        return {
            "id": self.id_get(),
            "description": self.description,

            "address": str(self.address),
            "family": self.family,
            "custom_fields": self.custom_fields.copy(),

            "status_id": self.status_id,
            "nat_inside_id": self.nat_inside_id,
            "nat_outside_id": self.nat_outside_id,

            "vrf_id": self.vrf_id,
        }
