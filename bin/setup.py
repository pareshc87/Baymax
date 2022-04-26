
import os
import json

# Generate 'environment.json' to configure Baymax for you environment.
# Credentials: username=<plain_text>, password=<encrypted_password>, key=<encryption_key>
# To generate encrypted password & encryption key use encrypt_passwd utility.
#
# 'TrueSight Console' contains "<key>":"<value>" pair where <key> is your environment and
#  <value> is truesight console URL (without trailing '/' at the end). You can configure
#  additional environment keys and URLs here.
#
#  "TSIM Servers" is  "<key>":"<value>" pair where <key> is your environment and
#  <value> is list of TSIM server's FQDN in each environment. You can configure
#  additional environment keys and TSIM servers list here.
#
# "Server Cells" is  "<key>":"<value>" pair where <key> is your environment and
#  <value> is list of server cell names e.g. pncell_<hostname> in each environment. You can configure
#  additional environment keys and server cells list here.
#
# "Event Cells" is list of remote cell names identified by key "Cells". Set "HA" as "True" or "False"
# if cells in list are in HA pair. Do not list #1 or #2 separately.

config_environment = {
    "username": "admin",
    "password": "encrypted_password",
    "key": "encrption_key",
    "TrueSight Console": {
        "QA": "https://abc.domain.com",
        "PROD": "https://abc.domain.com"
    },
    "TSIM Servers": {
        "QA": [
            "qa-tsim1.domain.com",
            "qa-tsim2.domain.com"
        ],
        "PROD": [
            "prod-tsim1.domain.com",
            "prod-tsim2.domain.com",
        ]
    },
    "Server Cells": {
        "QA": [
            "pncell_qa-tsim1",
            "pncell_qa-tsim2"
        ],
        "PROD": [
            "pncell_prod-tsim1",
            "pncell_prod-tsim2"
        ]
    },
    "Event Cells": {
        "HA": "True",
        "Cells": [
            "RemoteCell-HA-prod1",
            "RemoteCell-HA-prod2",
            "RemoteCell-HA-qa1",
            "RemoteCell-HA-qa2"
        ]}
}

# Generate 'configuration.json' that controls what data should baymax collect.
# Each parent key controls feature that Baymax can execute.
# You can turn any feature on/off by setting 'enabled' key to 'True' or 'False'
#
# There are other 'key' : 'value' pairs that contain essential data that baymax
# uses to make HTTP requests and/or gather information. DO NOT DELETE and/or MODIFY other
# keys & its values if you are not sure how it will affect Baymax's functionality.

config_baymax = {
    "managed_devices": {
        "enabled": "True",
        "data": {
            "stringToSearch": "",
            "fieldToSearch": "",
            "agentFilterCriteria": "",
            "directFilterCriteria": {
                "isConnected": "true",
                "isDisconnected": "true",
                "agentConnected": "true",
                "agentDisconnected": "true"
            }
        }
    },
    "performance_diagnostics": {
        "enabled": "True",
        "keys": [
            "Devices",
            "Monitor Instances",
            "Attributes"
        ]
    },
    "deployment_analysis_event_summary": {
        "enabled": "True"
    },
    "list_disconnected_agents": {
        "enabled": "True"
    }
}

if __name__ == '__main__':

    if not os.path.isdir(os.path.join(os.getcwd(), 'defaults')):
        os.mkdir(os.path.join(os.getcwd(), 'defaults'))

    # Create default 'environment.json' file
    env_filename = os.path.join(
        os.getcwd(), 'defaults') + '\\environment.json'
    with open(env_filename, 'w') as fh:
        json.dump(config_environment, fh)
        print(f'Created {env_filename} successfully.')

    # Create default 'configuration.json' file
    conf_filename = os.path.join(
        os.getcwd(), 'defaults') + '\\configuration.json'
    with open(conf_filename, 'w') as fh:
        json.dump(config_baymax, fh)
        print(f'Created {conf_filename} successfully.')
