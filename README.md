ipam-migrator working again
=============

This is a fork of Callum027/ipam-migrator with two bugfixes to make it working again in current (v3) Netbox environments. I think the original repo was abandoned at some point.

IPAM data migration tool for between phpIPAM and NetBox. Currently supports reading from phpIPAM and writing to NetBox.


Prerequisites
-------------

The following software packages are required to use the `Makefile` features:

* **make**
* **pylint**
* **pip**

The following Python modules are required to use `setup.py` to install ipam-migrator:

* **setuptools**

The following software packages are required to run ipam-migrator:

* **Python**, version **3.4** or later
* **requests**


Installation
------------

l3overlay can be installed to the default location by simply using:

    sudo make install

By default, this will install the executables into `/usr/local/sbin`.

See the `Makefile` for more details on how to change the installation locations.


Running
-------

Once ipam-migrator is installed and configured, it can be executed by simply running the `ipam-migrator` command if it is located in the `PATH` environment variable, or by running the executable directly if it is not.

The command `ipam-migrator --help` documents the optional arguments which can be used.

```
usage: ipam-migrator [-h] [-l FILE] [-ll LEVEL] [-iasv | -naisv]
                     [-oasv | -noasv]
                     INPUT-API-ENDPOINT,TYPE,AUTH-METHOD,KEY|TOKEN|USER,PASSWORD
                     [OUTPUT-API-ENDPOINT,TYPE,AUTH-METHOD,KEY|TOKEN|USER,PASSWORD]

Transfer IPAM information between two (possibly differing) systems

positional arguments:
  INPUT-API-ENDPOINT,TYPE,AUTH-METHOD,KEY|TOKEN|(USER,PASSWORD)
                        input database API endpoint, type, authentication
                        method and required information
  OUTPUT-API-ENDPOINT,TYPE,AUTH-METHOD,KEY|TOKEN|(USER,PASSWORD)
                        output database API endpoint, type, authentication
                        method and required information

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --log FILE   log output to FILE
  -ll LEVEL, --log-level LEVEL
                        use LEVEL as the logging level parameter
  -iasv, --input-api-ssl-verify
                        verify the input API endpoint SSL certificate
                        (default)
  -naisv, --no-input-api-ssl-verify
                        do NOT verify the input API endpoint SSL certificate
  -oasv, --output-api-ssl-verify
                        verify the output API endpoint SSL certificate
                        (default)
  -noasv, --no-output-api-ssl-verify
                        do NOT verify the output API endpoint SSL certificate
```

Specifying both an input and output API endpoint will migrate all data from the input to the output. Specifying just an input API endpoint will make ipam-migrator read all data from the input and output it to the logger, which is useful for verifying that the information being migrated to an output is correct before actually sending it.
