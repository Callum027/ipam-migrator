#
# IPAM database migration script
# ipam_migrator/db/vlan_group.py - database type for VLAN groups
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


from ipam_migrator.db.object import Object


class VLANGroup(Object):
    '''
    Database type for VLAN groups.
    '''


    def __init__(self,
                 vlan_group_id,
                 slug,
                 name=None,
                 status_id=None):
        '''
        VLAN group object constructor.
        '''

        super().__init__(vlan_group_id, name, None)

        self.slug = slug
        self.status_id = int(status_id) if status_id is not None else None


    def as_dict(self):
        '''
        '''

        return {
            "id": self.id_get(),
            "name": self.name,
            "description": self.description,

            "slug": self.slug,
            "status_id": self.status_id,
        }
