#
# Migrator tool for phpIPAM-NetBox
# migrator/db/ip/aggregate.py - Internet Protocol (IP) aggregate subnet prefixes
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
Internet Protocol (IP) aggregate subnet prefixes.
'''


import ipaddress

from migrator.db.object import Object


class Aggregate(Object):
    '''
    Database type for Internet Protocol (IP) aggregate subnet prefixes.
    '''


    def __init__(self,
                 aggregate_id,
                 prefix,
                 rir=None,
                 custom_fields=None,
                 name=None, description=None):
        '''
        VLAN object constructor.
        '''

        super.__init__(aggregate_id, name, description)

        self.prefix = ipaddress.ip_network(prefix)

        self.rir = rir

        self.custom_fields = dict(custom_fields)