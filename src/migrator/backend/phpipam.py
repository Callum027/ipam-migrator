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


class PhpIPAM(BaseBackend):
    '''
    '''


    def __init__(self,
                 api_endpoint, api_user, api_pass):
        '''
        '''

        # Configuration fields.
        self.api_endpoint = api_endpoint
        self.api_user = api_user
        self.api_pass = api_pass

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

        


    #
    ##
    #


    def api_authenticate(self):
        '''
        https://phpipam.net/api/api_documentation/
        2.1 Authentication
        '''

        if self.token and self.token_expires < datetime.utcnow():
            return

        req = requests.post(
            "{}/user".format(self.api_url),
            auth=requests.auth.HTTPBasicAuth(self.api_user, self.api_pass),
        )
        res = req.json()

        if bool(res["success"]):
            self.token = res["data"]["token"]
            # Example format: 2015-07-09 20:05:28
            self.token_expires = datetime.strptime(res["data"]["expires"], "%Y-%m-%d %H:%M:%S")
        else:
            raise RuntimeError(
                "failed to receive authentication token from phpIPAM: error {} ({})".format(
                    res["code"],
                    res["message"],
                ),
            )


    def api_read(self, *args, data=None):
        '''
        '''

        self.api_authenticate()

        request = "/".join(args)

        return requests.get(
            "{}/{}".format(self.api_endpoint, request),
            headers={"phpipam-token": self.token},
            data=data,
        )


    #
    ##
    #


    def sections_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.1 Sections controller
        '''

        req = self.api_read("sections")
        res = req.json()

        return res["data"]


    def vlans_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.5 VLAN controller
        '''

        vlans = {}

        req = self.api_read("vlan")
        res = req.json()

        for vlan_data in res["data"]:
            vlans[vlan_data["id"]] = VLAN(
                vlan_data["id"], # vlan_id
                vlan_data["number"], # vid
                name=vlan_data["name"],
                description=vlan_data["description"],
                # Unused: domainId - L2 domain identifier (default 1 – default domain)
            )

        return vlans


    def prefixes_read_from_vlans(self, vlans):
        '''
        https://phpipam.net/api/api_documentation/
        3.2 Subnets controller
        '''

        prefixes = {}

        for vlan_id in vlans.keys():
            req = self.api_read("devices", vlan_id)
            res = req.json()

            for subnet_data in res["data"]:
                prefixes[subnet_data["id"]] = Prefix(
                    subnet_data["id"], # prefix_id
                    "{}/{}".format(subnet_data["subnet"], subnet_data["mask"]), # prefix
                    name=subnet_data["name"],
                    description=subnet_data["description"],
                    vlan_id=subnet_data["vlanId"],
                    vrf_id=subnet_data["vrfId"],
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
            req = self.api_read("subnets", prefix_id, "addresses")
            res = req.json()

            for address_data in res["data"]:
                ip_addresses[address_data["id"]] = Address(
                    address_data["id"], # address_id
                    address_data["ip"], # address
                    description=addresses_data["description"],
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
