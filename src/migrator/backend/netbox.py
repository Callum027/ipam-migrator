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

from migrator.db.role import Role
from migrator.db.service import Service
from migrator.db.ip_address import IPAddress
from migrator.db.prefix import Prefix
from migrator.db.aggregate import Aggregate
from migrator.db.vlan import VLAN
from migrator.db.vlan_group import VLANGroup
from migrator.db.vrf import VRF


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

        for data in res["data"]:
            roles[data["id"]] = Role(
                data["id"], # role_id
                data["weight"], # weight
                slug=data["slug"],
                name=data["name"],
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

        for data in res["results"]:
            ip_addresses[data["id"]] = IPAddress(
                data["id"], # ip_address_id
                data["address"], # address
                description=data["description"],
                custom_fields=data["custom_fields"],
                status_id=data["status"]["value"] if "status" in data else None,
                nat_inside_id=data["nat_inside"]["id"] if "nat_inside" in data else None,
                nat_outside_id=data["nat_outside"]["id"] if "nat_outside" in data else None,
                interface_id=data["interface"]["id"] if "interface" in data else None,
                vrf_id=data["vrf"]["id"] if "vrf" indata else None,
                tenant_id=data["tenant"]["id"] if "tenant" in data else None,
            )

        return ip_addresses


    def prefixes_read(self):
        '''
        '''

        prefixes = {}

        req = self.api_read("ipam", "prefixes")
        res = req.json()

        for data in res["results"]:
            prefixes[data["id"]] = Prefix(
                data["id"], # prefix_id

                data["prefix"], # prefix

                is_pool=data["is_pool"],
                custom_fields=data["custom_fields"],

                name=data["name"],
                description=data["description"],

                role_id=data["role"]["id"] if "role" in data else None,
                status_id=data["status"]["value"] if "status" in data else None,
                vlan_id=data["vlan"]["id"] if "vlan" in data else None,
                vrf_id=data["vrf"]["id"] if "vrf" in data else None,
                tenant_id=data["tenant"]["id"] if "tenant" in data else None,
                site_id=data["site"]["id"] if "site" in data else None,
            )

        return prefixes


    def aggregates_read(self):
        '''
        '''

        aggregates = {}

        req = self.api_read("ipam", "aggregates")
        res = req.json()

        for data in res["results"]:
            aggregates[data["id"]] = Prefix(
                data["id"], # aggregate_id

                data["prefix"], # prefix

                rir=data["rir"],
                custom_fields=data["custom_fields"],

                description=data["description"],
            )

        return prefixes


    def vlans_read(self):
        '''
        '''

        vlans = {}

        req = self.api_read("ipam", "vlans")
        res = req.json()

        for data in res["results"]:
            vlan[data["id"]] = VLAN(
                data["id"], # vlan_id

                data["vid"], # vid

                name=data["name"],
                description=data["description"],

                status_id=data["status"]["value"] if "status" in data else None,
                group_id=data["group"]["id"] if "status" in data else None,
                tenant_id=data["tenant"]["id"] if "tenant" in data else None,
                site_id=data["site"]["id"] if "site" in data else None,
            )

        return vlans


    def vlan_groups_read(self):
        '''
        '''

        vlan_groups = {}

        req = self.api_read("ipam", "vlan-groups")
        res = req.json()

        for data in res["results"]:
            vlans[data["id"]] = VLANGroup(
                data["id"], # vlan_group_id

                slug=data["slug"], # slug

                name=data["name"],

                site_id=data["site"]["id"] if "site" in data else None,
            )

        return vlan_groups


    def vrfs_read(self):
        '''
        '''

        vrfs = {}

        req = self.api_read("ipam", "vlan-groups")
        res = req.json()

        for data in res["results"]:
            vrfs[data["id"]] = VRF(
                data["id"], # vrf_id

                data["rd"], # route_distinguisher
                enforce_unique=data["enforce_unique"], 

                name=data["name"],
                description=data["description"],

                site_id=data["site"]["id"] if "site" in data else None,
            )

        return vrfs
