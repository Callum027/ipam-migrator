#
# IPAM database migration script
# ipam_migrator/db/role.py - database type for roles
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


class Role(Object):
    '''
    Database type for Internet Protocol (IP) subnet prefixes.
    '''


    def __init__(self,
                 role_id,
                 weight, slug,
                 name=None, description=None):
        '''
        Role object constructor.
        '''

        # Initialise database object with ID.
        super().__init__(role_id, name, description)

        # Internal fields.
        self.weight = int(weight)
        self.slug = slug


    def as_dict(self):
        '''
        '''

        return {
            "id": self.id_get(),
            "name": self.name,
            "description": self.description,

            "weight": self.weight,
            "slug": self.slug,
        }
