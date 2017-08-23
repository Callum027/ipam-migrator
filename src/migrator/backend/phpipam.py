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


    def api_request(self, request, data=None):
        '''
        '''

        self.api_authenticate()

        return requests.get(
            "{}/{}".format(self.api_endpoint, request),
            headers={"phpipam-token": self.token},
            data=data,
        )


    def sections_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.1 Sections controller
        '''

        req = self.api_request("sections")
        res = req.json()

        return res["data"]


    def prefixes_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.2 Subnets controller
        '''

        req = self.api_request(
            "subnets/search/{}".format(self.api_url, self.api_key),
            data={
                "mac": self.mac,
                "hostname": self.hostname,
            },
        )


    def vlans_read(self):
        '''
        https://phpipam.net/api/api_documentation/
        3.2 VLAN controller
        '''

        vlans = []

        req = self.api_request("vlan")
        res = req.json()

        for vlan_data in res["data"]:
            vlans.append({
                # id - phpIPAM ID - Vlan identifier, identifies which vlan to work on.
                # domainId - L2 domain identifier (default 1 – default domain)
                # name - VLAN name
                # number - VLAN ID (number)
                # description - VLAN description
                # editDate - Date and time of last update
                "name": vlan_data["name"],
                "description": vlan_data["description"],

                "vlan_id": vlan_data["number"],

            })

            vlans.append(vlan)


    def read(self,
             read_sections=False,
             read_vlans=False,
             read_vrfs=False,
             read_prefixes=False,
             read_devices=False,
             read_addresses=False):
        '''
        '''

        database =

        if read_prefixes:
            

        if read_addresses:

        return database
