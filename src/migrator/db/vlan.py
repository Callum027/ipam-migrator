#
# Migrator tool for phpIPAM-NetBox
# migrator/db/vlan.py - database type for VLANs
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


class VLAN(object):
    '''
    Database type for VLANs.
    '''


    def __init__(self,
                 vlan_id, status=None,
                 name=None, description=None):
        '''
        VLAN object constructor.
        '''

        self.vlan_id = vlan_id
        self.status = status

        self.name = name
        self.description = description


    def __hash__(self):
        '''
        Hash function for VLAN object, based around the VLAN ID.
        '''

        return self.vlan_id


    def __lt__(self, other):
        '''
        Less-than function for VLAN object,
        implementing logical ordering based around the VLAN ID.
        '''

        return self.vlan_id < other.vlan_id


    def __le__(self, other):
        '''
        Less-than-or-equal-to function for VLAN object,
        implementing logical ordering based around the VLAN ID.
        '''

        return self.vlan_id <= other.vlan_id


    def __eq__(self, other):
        '''
        Equal function for VLAN object,
        implementing logical ordering based around the VLAN ID.
        '''

        return self.vlan_id == other.vlan_id


    def __ne__(self, other):
        '''
        Not-equal function for VLAN object,
        implementing logical ordering based around the VLAN ID.
        '''

        return self.vlan_id != other.vlan_id


    def __gt__(self, other):
        '''
        Greater-than function for VLAN object,
        implementing logical ordering based around the VLAN ID.
        '''

        return self.vlan_id > other.vlan_id


    def __ge__(self, other):
        '''
        Greater-than-or-equal-to function for VLAN object,
        implementing logical ordering based around the VLAN ID.
        '''

        return self.vlan_id >= other.vlan_id
