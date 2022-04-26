
import json
import urllib3

from time import sleep
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TrueSightConsole:

    # Init
    def __init__(self, env, session_) -> None:
        self.env = env
        self.session_ = session_

    # Authenticate TrueSight Presentation Console session
    def login(self, url, username, password) -> None:

        r = self.session_.get(url)
        soup = BeautifulSoup(r.text, features='html.parser')

        form_data = {input['name']: input['value']
                     for input in soup.form.find_all('input')}
        form_data['url_hash_handler'] = 'true'
        form_data['user-name'] = username
        form_data['password'] = password

        r = self.session_.post(url=soup.form['action'], data=form_data)
        r = self.session_.get(url)
        return None

    # Request 'Configuration > Managed Devices' APIs

    def managed_devices(self, url: str, data: str) -> str:

        url = f'{url}/tsws/10.0/api/unifiedadmin/Server/details?withCount=true'
        headers = {
            'Content-Type': 'application/json',
            'X-XSRF-TOKEN': self.session_.cookies['XSRF-TOKEN']
        }
        try:
            r = self.session_.post(url, headers=headers, data=data)
            if r.status_code == 200:
                return r.text
            else:
                return str(r.status_code)
        except:
            print('error!')

    # Request 'Monitored Data'
    def performance_diagnostics(self, tsim_server_fqdn: str, data: str) -> str:
        sleep(3)
        url = f'https://{tsim_server_fqdn}/jsp/PerformanceOptions.jsp'
        print(f'Fetch {url}')
        r = self.session_.post(url, data=data, verify=False)
        if r.status_code == 200:
            print('Received')
            return r.text
        else:
            print(f'Failed to get data from {url}')
            return str(r.status_code)

    # Request 'Detailed Event Summary'

    def get_max_alarm_details(self, tsim_server_fqdn: str):
        sleep(3)
        request_failed = True
        url = f'https://{tsim_server_fqdn}/jsp/DeploymentAnalysis-AsyncData.jsp?MaxAlarmDetails=1&ms=999'
        print(f'Fetch {url}')
        fail_counter = 0
        while request_failed:
            r = self.session_.get(url, verify=False)
            response_json = json.loads(r.text)
            if 'eventsPerDay' in response_json.keys():
                fail_counter = 0
                request_failed = False
                print('Received')
                return r.text
            else:
                sleep(2)
                fail_counter += 1
                print(f'Failed to recieve response from {url}. Retry {fail_counter}')

    def get_disconnected_agents(self, url: str, data: str):
        url = f'{url}/tsws/10.0/api/unifiedadmin/Server/details?withCount=true'
        print(f'Fetch {url}')
        headers = {
            'Content-Type': 'application/json',
            'X-XSRF-TOKEN': self.session_.cookies['XSRF-TOKEN']
        }
        try:
            r = self.session_.post(url, headers=headers, data=data)
            if r.status_code == 200:
                print('Received')
                return r.text
            else:
                print(f'Failed to recieve response from {url}')
                return str(r.status_code)
        except:
            print('Error!')
