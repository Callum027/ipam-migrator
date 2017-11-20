#
# IPAM database migration script
# ipam_migrator/db/vlan.py - database type for VLANs
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
Database type for VLANs.
'''


from ipam_migrator.db.object import Object


class VLAN(Object):
    '''
    Database type for VLANs.
    '''


    def __init__(self,
                 vlan_id,
                 vid,
                 name=None, description=None):
        '''
        VLAN object constructor.
        '''

        super().__init__(vlan_id, name, description)

        self.vid = int(vid)


    def __str__(self):
        '''
        String representation of a VLAN.
        '''

        if self.name:
            return "VLAN {} with name '{}'".format(self.vid, self.name)
        elif self.description:
            return "VLAN {} with description '{}'".format(self.vid, self.description)
        return "VLAN {}".format(self.vid)


    def as_dict(self):
        '''
        Dictionary representation of a VLAN.
        '''

        return {
            "id": self.id_get(),
            "name": self.name,
            "description": self.description,

            "vid": self.vid,
        }
