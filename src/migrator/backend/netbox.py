#
# Migrator tool for phpIPAM-NetBox
# migrator/backend/netbox.py - NetBox database backend
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
phpIPAM database backend.
'''


import datetime

import requests

from migrator.db.ip_address import IPAddress
from migrator.db.prefix import Prefix
from migrator.db.role import Role


class HTTPTokenAuth(requests.auth.AuthBase):
    '''
    Attaches HTTP Token Authentication to the given Request object.
    '''

    def __init__(self, token):
        '''
        '''

        self.token = token


    def __eq__(self, other):
        '''
        '''

        return self.token == other.token


    def __ne__(self, other):
        '''
        '''

        return self.token != other.token


    def __call__(self, req):
        '''
        '''

        req.headers["Authorization"] = "Token {}".format(self.token)
        return req


class NetBox(BaseBackend):
    '''
    '''


    def __init__(self,
                 api_endpoint, api_token):
        '''
        '''

        # Configuration fields.
        self.api_endpoint = api_endpoint
        self.api_token = api_token


    #
    ##
    #


    def database_read(self,
                      read_roles=True,
                      read_services=True,
                      read_ip_addresses=True,
                      read_prefixes=True,
                      read_aggregates=True,
                      read_vlans=True,
                      read_vlan_groups=True,
                      read_vrfs=True):
        '''
        '''

        # Reading VLANs are required for reading prefixes or IP addresses,
        # even if the VLANs themselves are not requested in the database.
        if read_vlans or read_prefixes or read_ip_addresses:
            vlans = self.vlans_read()
        else:
            vlans = tuple()

        # Reading prefixes are required for reading IP addresses,
        # even if the VLANs themselves are not requested in the database.
        if read_prefixes or read_ip_addresses:
            prefixes = self.prefixes_read_from_vlans(vlans)
        else:
            prefixes = tuple()

        if read_ip_addresses:
            ip_addresses = self.ip_addresses_read_from_prefixes(prefixes)
        else:
            ip_addresses = tuple()

        if read_vlan_groups:
            vlan_groups = self.vlan_groups_read()
        else:
            vlan_groups = tuple()

        if read_vrfs:
            vrfs = self.vrfs_read()
        else:
            vrfs = tuple()

        return Database(
            tuple(), # roles
            tuple(), # services
            ip_addresses,
            prefixes if read_prefixes else tuple(), # phpIPAM: Subnets
            tuple(), # aggregates
            vlans if read_vlans else tuple(),
            vlan_groups, # phpIPAM: L2 domains
            vrfs,
        )


    def database_write(self, database):
        '''
        '''

        pass


    #
    ##
    #


    def api_read(self, *args, data=None):
        '''
        '''

        request = "/".join(args)

        return requests.get(
            "{}/api/{}".format(self.api_endpoint, request),
            auth=HTTPTokenAuth(self.api_token),
            data=data,
        )


    def api_write(self, *args, data=None):
        '''
        '''

        request = "/".join(args)

        return requests.post(
            "{}/api/{}".format(self.api_endpoint, request),
            auth=HTTPTokenAuth(self.api_token),
            data=data,
        )


    #
    ##
    #


    def roles_read(self):
        '''
        '''

        roles = {}

        req = self.api_read("ipam", "roles")
        res = req.json()

        for role_data in res["data"]:
            roles[role_data["id"]] = Role(
                role_data["id"], # role_id
                role_data["weight"], # weight
                slug=role_data["slug"],
                name=role_data["name"],
            )

        return roles


    def services_read(self):
        '''
        '''

        pass


    def ip_addresses_read(self):
        '''
        '''

        ip_addresses = {}

        req = self.api_read("ipam", "ip-addresses")
        res = req.json()

        for ip_address_data in res["results"]:
            ip_addresses[address_data["id"]] = IPAddress(
                ip_address_data["id"], # address_id
                ip_address_data["address"], # address
                description=ip_address_data["description"],
                custom_fields=ip_address_data["custom_fields"],
                status_id=ip_address_data["status"]["value"]
                          if "status" in ip_address_data else None,
                nat_inside_id=ip_address_data["nat_inside"]["id"]
                              if "nat_inside" in ip_address_data else None,
                nat_outside_id=ip_address_data["nat_outside"]["id"]
                               if "nat_outside" in ip_address_data else None,
                interface_id=ip_address_data["interface"]["id"]
                             if "interface" in ip_address_data else None,
                vrf_id=ip_address_data["vrf"]["id"]
                       if "vrf" in ip_address_data else None,
                tenant_id=ip_address_data["tenant"]["id"]
                          if "tenant" in ip_address_data else None,
            )

        return ip_addresses


    def ip_addresses_read(self):
        '''
        '''

        prefixes = {}

        req = self.api_read("ipam", "prefixes")
        res = req.json()

        for prefix_data in res["results"]:
            prefixes[prefix_data["id"]] = Prefix(
                prefix_data["id"], # prefix_id
                prefix_data["prefix"], # prefix
                name=prefix_data["name"],
                description=prefix_data["description"],
                role_id=prefix_data["role"]["id"]
                          if "role" in prefix_data else None,
                status_id=prefix_data["status"]["value"]
                          if "status" in prefix_data else None,
                vlan_id=prefix_data["vlan"]["id"]
                       if "vlan" in prefix_data else None,
                vrf_id=prefix_data["vrf"]["id"]
                       if "vrf" in prefix_data else None,
                site_id=prefix_data["site"]["id"]
                          if "site" in prefix_data else None,
                tenant_id=prefix_data["tenant"]["id"]
                          if "tenant" in prefix_data else None,
            )

        return ip_addresses


    def aggregates_read(self):
        '''
        '''

        pass


    def vlans_read(self):
        '''
        '''

        pass


    def vlan_groups_read(self):
        '''
        '''

        pass


    def vrfs_read(self):
        '''
        '''

        pass
