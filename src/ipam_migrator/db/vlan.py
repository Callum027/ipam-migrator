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
                 name=None, description=None,
                 status_id=None):
        '''
        VLAN object constructor.
        '''

        self.__init__(vlan_id, name, description)

        self.vid = vid
        self.status_id = status_id


    def __str__(self):
        '''
        Human-readable stringifier method for VLANs,
        suitable for dumping to output.
        '''

        return self.object_str(
            vid=self.vid,
            status_id=self.status_id,
        )
