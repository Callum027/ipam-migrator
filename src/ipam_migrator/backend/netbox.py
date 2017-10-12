#
# IPAM database migration script
# ipam_migrator/backend/netbox.py - NetBox database backend
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
import json

import requests

from ipam_migrator.backend.base import BaseBackend

from ipam_migrator.db.aggregate import Aggregate
from ipam_migrator.db.ip_address import IPAddress
from ipam_migrator.db.prefix import Prefix
from ipam_migrator.db.role import Role
from ipam_migrator.db.vlan import VLAN
from ipam_migrator.db.vlan_group import VLANGroup
from ipam_migrator.db.vrf import VRF

from ipam_migrator.exception import APIReadError
from ipam_migrator.exception import APIWriteError
from ipam_migrator.exception import AuthMethodUnsupportedError


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


    def __init__(self, name, logger, api_endpoint, api_auth_method, api_auth_data, api_ssl_verify):
        '''
        '''

        super().__init__(name, logger)

        # Configuration fields.
        self.api_endpoint = api_endpoint

        self.token = None
        self.api_auth_method = api_auth_method
        if self.api_auth_method == "key":
            self.api_key = api_auth_data[0]
            self.api_token = None
        elif self.api_auth_method == "token":
            self.api_key = None
            self.api_token = api_auth_data[0]
        else:
            raise AuthMethodUnsupportedError(
                "netbox",
                api_auth_method,
                ("key", "token"),
            )

        self.api_ssl_verify = api_ssl_verify
        if not self.api_ssl_verify:
            # Try to uppress urllib3's InsecureRequestWarning.
            # disable_warnings is not available on all urllib3 versions.
            # Only call it if it is available.
            try:
                from urllib3 import disable_warnings
                from urllib3.exceptions import InsecureRequestWarning
                disable_warnings(InsecureRequestWarning)
            except ImportError:
                pass
            try:
                from requests.packages.urllib3 import disable_warnings
                from requests.packages.urllib3.exceptions import InsecureRequestWarning
                disable_warnings(InsecureRequestWarning)
            except ImportError:
                pass


    #
    ##
    #


    def database_read(self,
                      read_roles=True,
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
            roles,
            ip_addresses,
            prefixes if read_prefixes else tuple(),
            tuple(), # aggregates
            vlans if read_vlans else tuple(),
            vlan_groups, # phpIPAM: L2 domains
            vrfs,
        )


    def database_write(self, database):
        '''
        '''

        if database.roles:
            roles_old = database.roles
            roles_new, roles_old_to_new = self.roles_write(roles_old)

        if database.ip_addresses:
            ip_addresses_old = database.ip_addresses
            ip_addresses_new, ip_addresses_old_to_new = self.ip_addresses_write(ip_addresses_old)


    #
    ##
    #


    def api_authenticate(self):
        '''
        '''

        if self.api_key and not self.token:
            self.token = self.api_key
        elif self.api_token and not self.token:
            self.token = self.api_token
        else:
            raise RuntimeError(
                "unable to determine correct token for API endpoint '{}'".format(
                    self.api_endpoint,
                ),
            )


    def api_read(self, *args, data=None):
        '''
        '''

        self.api_authenticate()

        request = "/".join(args)

        return requests.get(
            "{}/{}".format(self.api_endpoint, request),
            auth=HTTPTokenAuth(self.token),
            data=data,
            verify=self.api_ssl_verify,
        ).json()


    def api_write(self, *args, data=None):
        '''
        '''

        self.api_authenticate()

        command = "/".join((str(a) for a in args))

        response = requests.post(
            "{}/{}/".format(self.api_endpoint, command),
            auth=HTTPTokenAuth(self.token),
            data=data,
            verify=self.api_ssl_verify,
        )

        if not response.text:
            raise APIReadError(response.status_code, "(empty response)")

        obj = response.json()

        if response.status_code == 201: # Created
            return obj
        elif response.status_code == 400: # Bad request
            raise APIWriteError(
                response.status_code,
                "bad request:\n{}".format(
                    "\n".join(("  {}: {}".format(k, v) for k, v in obj.items())),
                ),
            )
        else:
            raise APIWriteError(response.status_code, "(unhandled error code)")


    #
    ##
    #


    def roles_read(self):
        '''
        '''

        req = self.api_read("ipam", "roles")
        res = req.json()

        return {data["id"]:self.role_get(data) for data in res["results"]}


    def ip_addresses_read(self):
        '''
        '''

        req = self.api_read("ipam", "ip-addresses")
        res = req.json()

        return {data["id"]:self.ip_address_get(data) for data in res["results"]}


    def prefixes_read(self):
        '''
        '''

        req = self.api_read("ipam", "prefixes")
        res = req.json()

        return {data["id"]:self.prefix_get(data) for data in res["results"]}


    def aggregates_read(self):
        '''
        '''

        req = self.api_read("ipam", "aggregates")
        res = req.json()

        return {data["id"]:self.aggregate_get(data) for data in res["results"]}


    def vlans_read(self):
        '''
        '''

        req = self.api_read("ipam", "vlans")
        res = req.json()

        return {data["id"]:self.vlan_get(data) for data in res["results"]}


    def vlan_groups_read(self):
        '''
        '''

        vlan_groups = {}

        req = self.api_read("ipam", "vlan-groups")
        res = req.json()

        return {data["id"]:self.vlan_group_get(data) for data in res["results"]}


    def vrfs_read(self):
        '''
        '''

        vrfs = {}

        req = self.api_read("ipam", "vlan-groups")
        res = req.json()

        return {data["id"]:self.vrf_get(data) for data in res["results"]}


    #
    ##
    #


    def roles_write(self, roles):
        '''
        '''

        roles_old_to_new = dict()
        roles_new = dict()

        for role in roles.values():
            # Write object to NetBox.
            req = self.api_write(
                "ipam",
                "roles",
                data={
                    "name": role.name,
                    "weight": role.weight,
                    "slug": role.slug,                
                },
            )

            # Get returned NetBox object, with new ID.
            res = req.json()
            new_role = self.role_get(res["results"])
            new_roles[new_role.id] = new_role

            # Take old ID and new ID, and generate a mapping.
            id_old_new[role.id] = new_role.id

        return (roles_new, roles_old_to_new)


    def ip_addresses_write(self, ip_addresses):
        '''
        '''

        self.logger.info("Writing IP addresses...")

        count = 0

        ip_addresses_old_to_new = dict()
        ip_addresses_new = dict()

        for ip_address in ip_addresses.values():
            # Write object to NetBox, and get returned NetBox object, with new ID.
            new_ip_address = self.ip_address_get(
                self.api_write(
                    "ipam",
                    "ip-addresses",
                    data={
                        "description": ip_address.description,
                        "address": str(ip_address.address),
                        "custom-fields": ip_address.custom_fields,
                        # "status_id": ip_address.status_id,
                        # "nat_inside_id": ip_address.nat_inside_id,
                        # "nat_outside_id": ip_address.nat_outside_id,
                        # "vrf_id": ip_address.vrf_id,     
                    },
                )
            )
            new_ip_address[new_ip_address.id] = new_ip_address

            # Take old ID and new ID, and generate a mapping.
            ip_addresses_old_new[ip_address.id] = new_ip_address.id

            raise RuntimeError(json.dumps(new_ip_address.as_dict(), indent=4))
            count += 1

        self.logger.info("Wrote {} IP addresses.".format(count))

        return (ip_addresses_new, ip_addresses_old_to_new)


    #
    ##
    #


    def role_get(self, data):
        '''
        '''

        return Role(
            data["id"], # role_id
            data["weight"], # weight
            slug=data["slug"],
            name=data["name"],
        )


    def ip_address_get(self, data):
        '''
        '''

        return IPAddress(
            data["id"], # ip_address_id
            data["address"], # address
            description=data["description"],
            custom_fields=data["custom-fields"],
            status_id=data["status"]["value"] if "status" in data else None,
            nat_inside_id=data["nat_inside"]["id"] if "nat_inside" in data else None,
            nat_outside_id=data["nat_outside"]["id"] if "nat_outside" in data else None,
            interface_id=data["interface"]["id"] if "interface" in data else None,
            vrf_id=data["vrf"]["id"] if "vrf" in data else None,
            tenant_id=data["tenant"]["id"] if "tenant" in data else None,
        )


    def prefix_get(self, data):
        '''
        '''

        return Prefix(
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


    def aggregate_get(self, data):
        '''
        '''

        return Aggregate(
            data["id"], # aggregate_id
            data["prefix"], # prefix
            rir=data["rir"],
            custom_fields=data["custom_fields"],
            description=data["description"],
        )


    def vlan_get(self, data):
        '''
        '''

        return VLAN(
            data["id"], # vlan_id
            data["vid"], # vid
            name=data["name"],
            description=data["description"],
            status_id=data["status"]["value"] if "status" in data else None,
            group_id=data["group"]["id"] if "status" in data else None,
            tenant_id=data["tenant"]["id"] if "tenant" in data else None,
            site_id=data["site"]["id"] if "site" in data else None,
        )


    def vlan_group_get(self, data):
        '''
        '''

        return VLANGroup(
            data["id"], # vlan_group_id
            slug=data["slug"], # slug
            name=data["name"],
            site_id=data["site"]["id"] if "site" in data else None,
        )


    def vrf_get(self, data):
        '''
        '''

        return VRF(
            data["id"], # vrf_id
            data["rd"], # route_distinguisher
            enforce_unique=data["enforce_unique"], 
            name=data["name"],
            description=data["description"],
            site_id=data["site"]["id"] if "site" in data else None,
        )
