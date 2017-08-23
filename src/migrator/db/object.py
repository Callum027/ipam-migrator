#
# Migrator tool for phpIPAM-NetBox
# migrator/db/ip/subnet.py - Internet Protocol (IP) subnet prefixes
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


# Family 	IPv4
# VRF 	Global
# Tenant 	None
# Aggregate 	None
# Site 	None
# VLAN 	None
# Status 	Active
# Role 	None
# Is a pool     False
# Description 	N/A
# Utilization 	2 IP addresses (0%)


class Prefix(object):
    '''
    Database type for Internet Protocol (IP) subnet prefixes.
    '''


    def __init__(self, prefix,
                 name=None, description=None, role=None, status=None,
                 site=None, tenant=None, vlan=None, vrf=None,
                 is_a_pool=False, addresses=None):
        '''
        VLAN object constructor.
        '''

        self.prefix = ipaddress.ip_network(prefix)
        self.family = "IPv6" if isinstance(self.prefix, ipaddress.IPv6Network) else "IPv4"

        self.name = name
        self.description = description
        self.role = role
        self.status = status

        self.site = site
        self.tenant = tenant
        self.vlan = vlan
        self.vrf = vrf

        self.is_a_pool = is_a_pool
        self.addresses = list(addresses)


    def func_hash(self, key):
        '''
        Hash function for the Prefix object,
        based around the hash of the internal IPNetwork object.
        '''

        return self.__getattr__(key).__hash__()


    def compare(self, other, key, comparator):
        '''
        Less-than function for the Prefix object,
        implementing logical ordering based around the internal IPNetwork object.
        '''

        self_value = self.__getattr__(key)
        other_value = other.__getattr__(key)

        if not self.site.name == other.site.name:
            return self.site.name < other.site.name

        if self_value:
            if other_value is None:
                return 1
        elif not self_value:

        return self.prefix < other.prefix


    def __le__(self, other):
        '''
        Less-than-or-equal-to function for the Prefix object,
        implementing logical ordering based around the internal IPNetwork object.
        '''

        return self.prefix <= other.prefix


    def __eq__(self, other):
        '''
        Equal function for the Prefix object,
        implementing logical ordering based around the internal IPNetwork object.
        '''

        return self.prefix == other.prefix


    def __ne__(self, other):
        '''
        Not-equal function for the Prefix object,
        implementing logical ordering based around the internal IPNetwork object.
        '''

        return self.prefix != other.prefix


    def __gt__(self, other):
        '''
        Greater-than function for the Prefix object,
        implementing logical ordering based around the internal IPNetwork object.
        '''

        return self.prefix > other.prefix


    def __ge__(self, other):
        '''
        Greater-than-or-equal-to function for the Prefix object,
        implementing logical ordering based around the internal IPNetwork object.
        '''

        return self.prefix >= other.prefix
