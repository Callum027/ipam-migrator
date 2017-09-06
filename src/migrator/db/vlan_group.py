#
# Migrator tool for phpIPAM-NetBox
# migrator/db/vlan_group.py - database type for VLAN groups
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
Database type for VLAN groups.
'''


from migrator.db.object import Object


class VLANGroup(Object):
    '''
    Database type for VLAN groups.
    '''


    def __init__(self,
                 vlan_group_id,
                 slug=None,
                 name=None,
                 status_id=None):
        '''
        VLAN group object constructor.
        '''

        self.__init__(vlan_group_id, name, None)

        self.slug = slug if slug else name.lower().replace(" ", "-").replace("\t", "-")
        self.status_id = status_id


    def __str__(self):
        '''
        Human-readable stringifier method for VLAN groups,
        suitable for dumping to output.
        '''

        return self.object_str(
            slug=self.slug,
            status_id=self.status_id,
        )
