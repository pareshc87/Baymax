
import os
import json

from cryptography.fernet import Fernet


class DataProvider:

    def __init__(self, env) -> None:
        self.env = env
        filename = os.path.join(os.getcwd(), 'environment.json')
        with open(filename, 'r') as fh:
            self.data = json.load(fh)

    def get_user(self) -> str:
        return self.data[self.env]['username']

    def get_passwd(self) -> str:
        f = Fernet(self.data[self.env]['key'].encode())
        return f.decrypt(self.data[self.env]['password'].encode()).decode()

    def get_console_url(self) -> str:
        return self.data[self.env]['truesightConsoleURL']

    def get_servers(self) -> list:
        return self.data[self.env]['tsimServer']['fqdn']

    def get_server_cells(self) -> list:
        return self.data[self.env]['serverCellList']

    def get_pronet_config(self):
        return self.data[self.env]['pronetConfig']

    def is_remote_cell_ha(self) -> bool:
        return self.data[self.env]['remoteCell']['highAvailability']

    def get_remote_cells(self) -> list:
        return self.data[self.env]['remoteCell']['list']

    def get_pronet_instance_max(self):
        return (self.data[self.env]['tsimServer']['pronetConfig']['pronet.instance.large.max'])
