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


import requests

from ipam_migrator.backend.base import BaseBackend

from ipam_migrator.db.database import Database
from ipam_migrator.db.ip_address import IPAddress
from ipam_migrator.db.prefix import Prefix
from ipam_migrator.db.vlan import VLAN
from ipam_migrator.db.vrf import VRF

from ipam_migrator.exception import APIGetError
from ipam_migrator.exception import APIReadError
from ipam_migrator.exception import APIWriteError
from ipam_migrator.exception import AuthMethodUnsupportedError


class HTTPTokenAuth(requests.auth.AuthBase):
    '''
    Attaches HTTP Token Authentication to the given Request object.
    '''


    # pylint: disable=too-few-public-methods


    def __init__(self, token):
        '''
        HTTPTokenAuth object constructor.
        '''

        self.token = token


    def __eq__(self, other):
        '''
        HTTPTokenAuth equality checking method.
        '''

        return self.token == other.token


    def __ne__(self, other):
        '''
        HTTPTokenAuth non-equality checking method.
        '''

        return self.token != other.token


    def __call__(self, req):
        '''
        HTTPTokenAuth calling method.
        '''

        req.headers["Authorization"] = "Token {}".format(self.token)
        return req


class NetBox(BaseBackend):
    '''
    NetBox API backend.
    '''


    # pylint: disable=too-many-public-methods


    # pylint: disable=too-many-arguments
    def __init__(self,
                 logger, name,
                 api_endpoint, api_auth_method,
                 api_auth_data, api_ssl_verify):
        '''
        NetBox API backend constructor.
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


    def api_authenticate(self):
        '''
        Authenticate with the API backend.
        '''

        if self.token:
            return
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


    def api_get(self, uri):
        '''
        Send a GET request to the API backend.
        '''

        self.api_authenticate()

        response = requests.get(uri, auth=HTTPTokenAuth(self.token), verify=self.api_ssl_verify)

        if not response.text:
            raise APIReadError(response.status_code, "(empty response)")

        obj = response.json()

        if response.status_code == 200: # OK
            return obj["results"]
        elif response.status_code == 400: # Bad request
            raise APIGetError(
                response.status_code,
                "bad request:\n{}".format(
                    "\n".join(("  {}: {}".format(k, v) for k, v in obj.items())),
                ),
            )
        else:
            raise APIGetError(response.status_code, "(unhandled error code)")


    def api_read(self, *args):
        '''
        Read an object from the API backend.
        '''

        command = "/".join((str(a) for a in args))

        return self.api_get("{}/{}/".format(self.api_endpoint, command))


    def api_search(self, *args, **kwargs):
        '''
        Search for objects on the API backend.
        '''

        link = "/".join(args)
        params = "&".join(["{}={}".format(k, v) for k, v in kwargs.items()])
        command = "{}/?{}".format(link, params)

        return self.api_get("{}/{}".format(self.api_endpoint, command))


    def api_write(self, *args, data=None):
        '''
        Write an object to the API backend.
        '''

        self.api_authenticate()

        req_type = args[0]
        if req_type != "POST" and req_type != "PUT":
            raise APIWriteError(0, "request type '{}' unsupported by api_write".format(req_type))

        function = requests.put if req_type == "PUT" else requests.post
        command = "/".join((str(a) for a in args[1:]))
        uri = "{}/{}/".format(self.api_endpoint, command)

        response = function(
            uri,
            auth=HTTPTokenAuth(self.token),
            data=data,
            verify=self.api_ssl_verify,
        )

        if not response.text:
            raise APIReadError(response.status_code, "(empty response)")

        obj = response.json()

        if response.status_code == 200: # OK
            if req_type == "POST":
                raise APIWriteError(
                    0,
                    "received 200 (OK) response on a POST request, was expecting 201 (Created), "
                    "check that the request is not being converted from a POST to a GET "
                    "(e.g. when being redirected from HTTP to HTTPS), URI: {}".format(uri),
                )
            return obj
        if response.status_code == 201: # Created
            return obj
        elif response.status_code == 400: # Bad Request
            raise APIWriteError(
                response.status_code,
                "bad request:\n{}".format(
                    "\n".join(("  {}: {}".format(k, v) for k, v in obj.items())),
                ),
            )
        elif response.status_code == 405: # Method Not Allowed
            raise APIWriteError(
                response.status_code,
                "method not allowed at URI '{}', is the right URI being accessed?".format(
                    uri,
                ),
            )
        else:
            raise APIWriteError(response.status_code, "(unhandled error code)")


    def api_put(self, *args, data=None):
        '''
        Send a PUT request to the API backend.
        '''

        return self.api_write("PUT", *args, data=data)


    def api_post(self, *args, data=None):
        '''
        Send a POST request to the API backend.
        '''

        return self.api_write("POST", *args, data=data)


    #
    ##
    #


    def database_read(self,
                      read_ip_addresses=True,
                      read_prefixes=True,
                      read_vlans=True,
                      read_vrfs=True):
        '''
        Read a Database object from the API backend.
        '''

        vlans = self.vlans_read() if read_vlans else None
        vrfs = self.vrfs_read() if read_vrfs else None
        prefixes = self.prefixes_read() if read_prefixes else None
        ip_addresses = self.ip_addresses_read() if read_ip_addresses else None

        return Database(
            self.name,
            ip_addresses=ip_addresses,
            prefixes=prefixes,
            vlans=vlans,
            vrfs=vrfs,
        )


    def vlans_read(self):
        '''
        Read a dictionary of VLAN objects from the API backend.
        '''

        req = self.api_read("ipam", "vlans")
        res = req.json()

        return {data["id"]:self.vlan_get(data) for data in res["results"]}


    def vrfs_read(self):
        '''
        Read a dictionary of VRF objects from the API backend.
        '''

        req = self.api_read("ipam", "vrfs")
        res = req.json()

        return {data["id"]:self.vrf_get(data) for data in res["results"]}


    def prefixes_read(self):
        '''
        Read a dictionary of Prefix objects from the API backend.
        '''

        req = self.api_read("ipam", "prefixes")
        res = req.json()

        return {data["id"]:self.prefix_get(data) for data in res["results"]}


    def ip_addresses_read(self):
        '''
        Read a dictionary of IPAddress objects from the API backend.
        '''

        req = self.api_read("ipam", "ip-addresses")
        res = req.json()

        return {data["id"]:self.ip_address_get(data) for data in res["results"]}


    #
    ##
    #


    def database_write(self, database):
        '''
        Write a Database object to the API backend.
        '''

        # pylint: disable=unused-variable

        if database.vlans:
            vlans_old = database.vlans
            vlans_new, vlans_old_to_new = self.vlans_write(vlans_old)
        else:
            vlans_old = {}
            vlans_new = {}
            vlans_old_to_new = {}

        if database.vrfs:
            vrfs_old = database.vrfs
            vrfs_new, vrfs_old_to_new = self.vrfs_write(vrfs_old)
        else:
            vrfs_old = {}
            vrfs_new = {}
            vrfs_old_to_new = {}

        if database.prefixes:
            prefixes_old = database.prefixes
            prefixes_new, prefixes_old_to_new = self.prefixes_write(
                prefixes_old,
                vlans_new, vlans_old_to_new,
                vrfs_new, vrfs_old_to_new,
            )
        else:
            prefixes_old = {}
            prefixes_new = {}
            prefixes_old_to_new = {}

        if database.ip_addresses:
            ip_addresses_old = database.ip_addresses
            ip_addresses_new, ip_addresses_old_to_new = self.ip_addresses_write(
                ip_addresses_old,
                vrfs_new, vrfs_old_to_new,
            )
        else:
            ip_addresses_old = {}
            ip_addresses_new = {}
            ip_addresses_old_to_new = {}


    def obj_write(self,
                  obj_type,
                  obj_search_params,
                  obj_data,
                  obj_get_func):
        '''
        Write an Object to the API backend.
        '''

        # Check if an equivalent object already exists on NetBox.
        # If there is one, we will overwrite its data and reuse its ID
        # with a PUT request, otherwise upload a new object using a POST request.
        current_objs = self.api_search("ipam", obj_type, **obj_search_params)
        current_obj = current_objs[0] if current_objs else None

        if current_obj:
            new_obj_data = self.api_put(
                "ipam", obj_type, current_obj["id"],
                data=obj_data,
            )
        else:
            new_obj_data = self.api_post("ipam", obj_type, data=obj_data)
        new_obj = obj_get_func(new_obj_data)

        if current_obj:
            self.logger.debug("updated {}".format(new_obj))
        else:
            self.logger.debug("wrote {}".format(new_obj))

        return new_obj


    def vrfs_write(self, vrfs):
        '''
        Write a dictionary of VRF objects to the API backend.
        '''

        raise NotImplementedError()


    def vlans_write(self, vlans):
        '''
        Write a dictionary of VLAN objects to the API backend.
        '''

        self.logger.info("Writing VLANs...")

        count = 0

        vlans_new = dict()
        vlans_old_to_new = dict()

        for vlan in vlans.values():
            new_vlan = self.obj_write(
                "vlans",
                {"vid": vlan.vid},
                {
                    "name": vlan.name,
                    "description": vlan.description,
                    "vid": vlan.vid,
                },
                self.vlan_get,
            )

            vlans_new[new_vlan.id_get()] = new_vlan
            vlans_old_to_new[vlan.id_get()] = new_vlan.id_get()

            count += 1

        self.logger.info("Wrote {} VLANs.".format(count))

        return (vlans_new, vlans_old_to_new)


    # pylint: disable=unused-argument
    def prefixes_write(self,
                       prefixes,
                       vlans_new, vlans_old_to_new,
                       vrfs_new, vrfs_old_to_new):
        '''
        Write a dictionary of Prefix objects to the API backend,
        using previously written VRFs and VLANs to preserve reference
        information.
        '''

        self.logger.info("Writing prefixes...")

        count = 0

        prefixes_new = dict()
        prefixes_old_to_new = dict()

        for prefix in prefixes.values():
            new_prefix = self.obj_write(
                "prefixes",
                {"q": str(prefix.prefix)},
                {
                    "description": prefix.description,
                    "prefix": str(prefix.prefix),
                    "is_pool": prefix.is_pool,
                    "vlan": vlans_old_to_new[prefix.vlan_id] if prefix.vlan_id else None,
                    "vrf": vrfs_old_to_new[prefix.vrf_id] if prefix.vrf_id else None,
                },
                self.prefix_get,
            )

            prefixes_new[new_prefix.id_get()] = new_prefix
            prefixes_old_to_new[prefix.id_get()] = new_prefix.id_get()

            count += 1

        self.logger.info("Wrote {} prefixes.".format(count))

        return (prefixes_new, prefixes_old_to_new)


    def ip_addresses_write(self,
                           ip_addresses,
                           vrfs_new, vrfs_old_to_new):
        '''
        Write a dictionary of IPAddress objects to the API backend,
        using previously written VRFs to preserve reference
        information.
        '''

        self.logger.info("Writing IP addresses...")

        count = 0

        ip_addresses_new = dict()
        ip_addresses_old_to_new = dict()

        for ip_address in ip_addresses.values():
            new_ip_address = self.obj_write(
                "ip-addresses",
                {"q": str(ip_address.address)},
                {
                    "description": ip_address.description,
                    "address": str(ip_address.address),
                    "custom_fields": ip_address.custom_fields,
                    "vrf": vrfs_old_to_new[ip_address.vrf_id] if ip_address.vrf_id else None,
                },
                self.ip_address_get,
            )

            ip_addresses_new[new_ip_address.id_get()] = new_ip_address
            ip_addresses_old_to_new[ip_address.id_get()] = new_ip_address.id_get()

            count += 1

        self.logger.info("Wrote {} IP addresses.".format(count))

        return (ip_addresses_new, ip_addresses_old_to_new)


    #
    ##
    #


    @staticmethod
    def object_id_get(data, key):
        '''
        Get an object ID from the given key in the data dictionary.
        '''

        if isinstance(data[key], int):
            return data[key]
        return data[key]["id"] if key in data and data[key] is not None else None


    @staticmethod
    def ip_address_get(data):
        '''
        Get an IPAddress object from the given data dictionary.
        '''

        return IPAddress(
            data["id"], # ip_address_id
            data["address"].split("/")[0], # address
            description=data["description"],
            custom_fields=data["custom_fields"] if "custom_fields" in data else None,
            vrf_id=NetBox.object_id_get(data, "vrf"),
        )


    @staticmethod
    def prefix_get(data):
        '''
        Get a Prefix object from the given data dictionary.
        '''

        return Prefix(
            data["id"], # prefix_id
            data["prefix"], # prefix
            is_pool=data["is_pool"],
            description=data["description"],
            vlan_id=NetBox.object_id_get(data, "vlan"),
            vrf_id=NetBox.object_id_get(data, "vrf"),
        )


    @staticmethod
    def vlan_get(data):
        '''
        Get a VLAN object from the given data dictionary.
        '''

        return VLAN(
            data["id"], # vlan_id
            data["vid"], # vid
            name=data["name"],
            description=data["description"],
        )


    @staticmethod
    def vrf_get(data):
        '''
        Get a VRF object from the given data dictionary.
        '''

        return VRF(
            data["id"], # vrf_id
            data["rd"], # route_distinguisher
            enforce_unique=data["enforce_unique"],
            name=data["name"],
            description=data["description"],
        )
