#
# Migrator tool for phpIPAM-NetBox
# migrator/backend/phpipam.py - phpIPAM database backend
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

from ipam_migrator.backend.base import BaseBackend

from ipam_migrator.exception import APIOptionsError
from ipam_migrator.exception import APIReadError
from ipam_migrator.exception import AuthMethodUnsupportedError


class PhpIPAM(BaseBackend):
    '''
    '''


    def __init__(self, api_endpoint, api_auth_method, api_auth_data, api_ssl_verify):
        '''
        '''

        # Configuration fields.
        self.api_endpoint = api_endpoint

        self.api_auth_method = api_auth_method
        if self.api_auth_method == "login":
            self.api_user = api_auth_data[0]
            self.api_pass = api_auth_data[1]
        else:
            raise AuthMethodUnsupportedError(
                "phpipam",
                self.api_auth_method,
                ("login",),
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


        # Runtime fields.
        self.token = None
        self.token_expires = None

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


    def api_authenticate(self):
        '''
        https://phpipam.net/api/api_documentation/
        2.1 Authentication
        '''

        if self.token and not self.token_expires:
            return
        elif self.token and \
             self.token_expires and self.token_expires >= datetime.datetime.utcnow():
            return
        else:
            response = requests.post(
                "{}/user/".format(self.api_endpoint),
                auth=requests.auth.HTTPBasicAuth(self.api_user, self.api_pass),
                verify=self.api_ssl_verify,
            )

            if not response.text:
                raise RuntimeError("ERROR {}: (empty response)".format(response.status_code))
            elif response.text == "Authentication failed":
                raise RuntimeError("ERROR {}: authentication failed".format(response.status_code))

            obj = response.json()

            if obj["success"]:
                self.token = obj["data"]["token"]
                # Example format: 2015-07-09 20:05:28
                self.token_expires = datetime.datetime.strptime(
                    obj["data"]["expires"],
                    "%Y-%m-%d %H:%M:%S",
                )
            else:
                raise RuntimeError(
                    "ERROR {}: failed to receive authentication token from phpIPAM ({})".format(
                        obj["code"],
                        obj["message"],
                    ),
                )


    def api_read(self, *args, data=None):
        '''
        '''

        self.api_authenticate()

        command = "/".join((str(a) for a in args))

        response = requests.get(
            "{}/{}/".format(self.api_endpoint, command),
            headers={"phpipam-token": self.token},
            data=data,
            verify=self.api_ssl_verify,
        )

        if not response.text:
            raise APIReadError(response.status_code, "(empty response)")

        obj = response.json()

        if not obj["success"]:
            raise APIReadError(obj["code"], obj["message"])

        return obj["data"]


    def api_controller_methods(self, *args):
        '''
        '''

        self.api_authenticate()

        command = "/".join((str(a) for a in args))

        response = requests.options(
            "{}/{}/".format(self.api_endpoint, command),
            headers={"phpipam-token": self.token},
            verify=self.api_ssl_verify,
        )

        if not response.text:
            raise APIOptionsError(response.status_code, "(empty response)")

        obj = response.json()

        if not obj["success"]:
            raise APIOptionsError(obj["code"], obj["message"])

        # Create a dict which keys a command tuple with its available methods.
        #
        # Example dict:
        # {
        #   # https://ipam.example.com/api/example/vlans
        #   ("vlans",): ["OPTIONS", "GET"],
        #   # https://ipam.example.com/api/example/vlans/{id}
        #   ("vlans", "{id}"): ["GET", "POST", "PATCH", "DELETE"],
        # }
        command_methods = {}
        for href_methods in obj["data"]["methods"]:
            href = href_methods["href"]
            command = tuple(href.strip("/").split("/"))[2:]
            methods = href_methods["methods"]
            command_methods[command] = (met["method"] for met in methods)

        return command_methods


    #
    ##
    #


    def sections_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.1 Sections controller
        '''

        obj = self.api_read("sections")

        return obj["data"]


    def vlans_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.5 VLAN controller
        '''

        # GET command for the VLANs controller is not supported in phpIPAM
        # versions older than 1.3. It's much faster, though, so use it if
        # it's available.
        if "GET" in self.api_controller_methods("vlans")[("vlans",)]:
            return {data["id"]:self.vlan_get(data) for data in self.api_read("vlans")}
        else:
            vlans = {}
            for i in range(1, 4095):
                try:
                    data = self.api_read("vlans", i)
                    print(data)
                    vlans[i] = self.vlan_get(data)
                except APIReadError as err:
                    if err.api_code == 404 or err.api_message == "Vlan not found":
                        continue
                    else:
                        pass
            return vlans


    def prefixes_read_from_vlans(self, vlans):
        '''
        https://phpipam.net/api/api_documentation/
        3.2 Subnets controller
        '''

        prefixes = {}

        for vlan_id in vlans.keys():
            obj= self.api_read("devices", vlan_id)

            for data in obj["data"]:
                prefixes[data["id"]] = Prefix(
                    data["id"], # prefix_id
                    "{}/{}".format(data["subnet"], data["mask"]), # prefix
                    name=data["name"],
                    description=data["description"],
                    vlan_id=data["vlanId"],
                    vrf_id=data["vrfId"],
                    # Unused:
                    # sectionId - Section identifier (mandatory on add method).
                    # linked_subnet - Linked IPv6 subnet
                    # masterSubnetId - Master subnet id for nested subnet (default: 0)
                    # nameserverId - Id of nameserver to attach to subnet (default: 0)
                    # showName - Controls weather subnet is displayed as IP address or
                    #            Name in subnets menu (default: 0)
                    # permissions - Group permissions for subnet.
                    # DNSrecursive - Controls if PTR records should be created for subnet
                    #                (default: 0)
                    # DNSrecords - Controls weather hostname DNS records are displayed (default: 0)
                    # allowRequests - Controls if IP requests are allowed for subnet (default: 0)
                    # scanAgent - Controls which scanagent to use for subnet (default: 1)
                    # pingSubnet - Controls if subnet should be included in status checks
                    #            - (default: 0)
                    # discoverSubnet - Controls if new hosts should be discovered for new host
                    #                  scans (default: 0)
                    # isFolder - Controls if we are adding subnet or folder (default: 0)
                    # isFull - Marks subnet as used (default: 0)
                    # state - Assignes state (tag) to subnet (default: 1 – Used)
                    # threshold - Subnet threshold
                    # location - Location index
                    # editDate - Date and time of last update
                )

        return prefixes


    def ip_addresses_read_from_prefixes(self, prefixes):
        '''
        https://phpipam.net/api/api_documentation/
        3.4 Addresses controller
        '''

        ip_addresses = {}

        for prefix_id in prefixes.keys():
            obj = self.api_read("subnets", prefix_id, "addresses")

            for data in obj["data"]:
                ip_addresses[data["id"]] = Address(
                    data["id"], # address_id
                    data["ip"], # address
                    description=data["description"],
                    # Unused:
                    # subnetId - Id of subnet address belongs to
                    # is_gateway - Defines if address is presented as gateway
                    # hostname - Address hostname
                    # mac - Mac address
                    # owner - Address owner
                    # tag - IP tag (online, offline, ...)
                    # PTRignore - Controls if PTR should not be created
                    # PTR - Id of PowerDNS PTR record
                    # deviceId - Id of device address belongs to
                    # port - Port
                    # note - Note
                    # lastSeen - Date and time address was last seen with ping.
                    # excludePing - Exclude this address from status update scans (ping)
                    # editDate - Date and time of last update
                )

        return ip_addresses


    def vrfs_read(self):
        '''
        Not implemented.

        https://phpipam.net/api/api_documentation/
        3.7 VRF controller
        '''

        return tuple()


    def devices_read(self):
        '''
        Not implemented.

        https://phpipam.net/api/api_documentation/
        3.8 Devices controller
        '''

        return tuple()


    #
    ##
    #


    def sections_write(self):
        '''
        '''

        raise NotImplementedError()


    #
    ##
    #

    def vlan_get(self, data):
        '''
        '''

        return VLAN(
            data["id"], # vlan_id
            data["number"], # vid
            name=data["name"],
            description=data["description"],
            # Unused: domainId - L2 domain identifier (default 1 – default domain)
        )
