
import dis
import os
import sys
import json
import logging

from argparse import ArgumentParser
from requests import Session
from bs4 import BeautifulSoup
from datetime import datetime
from itertools import repeat
from bluecore.data_provider import DataProvider
from bluecore.event_cell_cli import EventCellCLI
from bluecore.persistence_manager import PersistenceManager
from bluecore.tsps import TrueSightConsole
from bluecore.postman import Postman
from bluecore.html_writer import HTMLWriter


class Baymax:

    def __init__(self, env: str) -> None:
        self.env = env

        with open(os.path.join(os.getcwd(), 'configuration.json'), 'r') as fh:
            self.config = json.load(fh)

        if not os.path.isdir(os.path.join(os.getcwd(), 'log')):
            os.mkdir('.\\log')
        else:
            log_file = os.getcwd() + \
                '_'.join(
                [f'\\log\\baymax_log[{env}]', datetime.now().strftime('%m%d%Y')]) + '.log'
            logging.basicConfig(
                filename=log_file,
                filemode='w',
                encoding='utf-8',
                datefmt="%m/%d/%Y %I:%M:%S %p",
                format='%(asctime)s %(levelname)s: %(message)s',
                level=logging.INFO
            )

    def isDevicesCountOn(self) -> bool:
        if self.config['managed_devices']['enabled'] == 'True':
            self.data = json.dumps(self.config['managed_devices']['data'])
            return True
        else:
            return False

    def isCapacityMetricsOn(self) -> bool:
        if self.config['performance_diagnostics']['enabled'] == 'True':
            self.keys = self.config['performance_diagnostics']['keys']
            return True
        else:
            return False

    def isGetMaxAlarmDetailsOn(self) -> bool:
        if self.config['deployment_analysis_event_summary']['enabled'] == 'True':
            return True
        else:
            return False

    def isDisconnectedAgentsOn(self) -> bool:
        if self.config['list_disconnected_agents']['enabled'] == 'True':
            self.data = json.dumps(
                self.config['list_disconnected_agents']['data'])
            return True
        else:
            return False


if __name__ == '__main__':

    # Below is fix for
    # OSError: Could not find a suitable TLS CA certificate bundle,
    # invalid path: C:\Users\PCHAUD~1\AppData\Local\Temp\_MEI85802\certifi\cacert.pem

    def override_where():
        """ overrides certifi.core.where to return actual location of cacert.pem"""
        # change this to match the location of cacert.pem
        return os.path.abspath("cacert.pem")

    # Is the program compiled?
    if hasattr(sys, "frozen"):
        import certifi.core

        os.environ["REQUESTS_CA_BUNDLE"] = override_where()
        certifi.core.where = override_where

        # delay importing until after where() has been replaced
        import requests.utils
        import requests.adapters
        # replace these variables in case these modules were
        # imported before we replaced certifi.core.where
        requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
        requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()

    # Create argument parser and parse arguments
    parser = ArgumentParser()
    parser.add_argument(
        '-e',
        metavar='Environment',
        type=str,
        choices=['QA', 'PROD'],
        default='QA', help='specify the environment in which TSOM is deployed')
    args = parser.parse_args()
    env = args.e.upper()
    env = env.lower()

    # Baymax gets configuration from 'configuration.json'
    baymax = Baymax(env)
    # DataProvider gets information about environment from 'environment.json'
    dp = DataProvider(env)
    # PersistenceManager to perform CRUD operation on data files in '/var' directory
    pm = PersistenceManager(env)
    # Call HTMLWriter to generate prod-report-<date>.html
    html_writer = HTMLWriter(env)
    # Configure and start logging progress
    logging.info("Hello! I'm Baymax")
    logging.info('Configuration File = "configuration.json"')
    logging.info('Environment = %s', env)

    with Session() as s:

        # Create TrueSight Console Object
        ts_console = TrueSightConsole(env, s)
        # Aunthenticate user session
        ts_console.login(dp.get_console_url(),
                         dp.get_user(), dp.get_passwd())
        # Check if user login is successful
        if set(['saml_token', 'JSESSIONID', 'XSRF-TOKEN']).issubset(set(s.cookies.keys())):
            logging.info('TrueSight Console - Authentication Successfull')
        else:
            logging.error('TrueSight Console - Authentication Failed!')
            print(
                'TrueSight Console - Authentication Failed!\nInvalid Username or Password')
            exit()

            # Collect capacity metrics from all TSIMs connected to TSOM from
        # 'TrueSight Console -> Configuration -> Managed Devices -> TSIM -> Performance Diagnostics'
        if baymax.isCapacityMetricsOn():
            data = f"authToken={s.cookies['saml_token']}&X-XSRF-TOKEN={s.cookies['XSRF-TOKEN']}"
            response_html_list = list(
                map(ts_console.performance_diagnostics, dp.get_servers(), repeat(data)))

            monitored_data_list = []
            for response_html in response_html_list:
                soup = BeautifulSoup(response_html, features='html.parser')
                with open('temp.html', 'w') as f:
                    f.write(str(soup))
                rows = soup.find('table', {'class': 'data'}).tbody.find_all(
                    'tr', {'class': 'data'})
                cols = [attrs for row in rows for attrs in row.find_all('td', {
                    'class': 'data'})]
                monitored_data = {cols[i].text.strip(
                ): cols[i+1].text.strip() for i in range(0, len(cols), 2)}
                monitored_data_list.append(monitored_data)

            capacity_data = []
            for monitored_data in monitored_data_list:
                capacity_data.append([monitored_data[key]
                                      for key in getattr(baymax, 'keys')])

            logging.info('Writing monitored data')
            # pm.write_monitored_data(capacity_data)
            html_writer.monitored_data_html(
                getattr(baymax, 'keys'), dp.get_servers(), capacity_data)

        # Collect Average Events/Day (5 Days) (External + Internal) events from
        # 'TrueSight Console -> Configuration -> Managed Devices -> TSIM
        # -> Performance Diagnostics -> Detail Event Summary'
        if baymax.isGetMaxAlarmDetailsOn():
            response_json_list = map(
                ts_console.get_max_alarm_details, dp.get_servers())
            event_per_day_list = [json.loads(response_json)[
                'eventsPerDay'] for response_json in response_json_list]

            logging.info('Writing Average events/day for 5days')
            # pm.write_avg_events_day_5_days(event_per_day_list)
            html_writer.avg_events_per_day(event_per_day_list)

        # Check if both Capacity Summary & Detail Event Summary is enabled, if yes
        # join columns from separate files in one and clean-up files
        if baymax.isCapacityMetricsOn() and baymax.isGetMaxAlarmDetailsOn():
            capacity_and_event_data = [capacity_data[i] + [event_per_day_list[i]]
                                       for i in range(len(dp.get_servers()))]

            logging.info(
                'Consolidate monitored data and Average events/day for 5days')
            pm.write_monitored_data_and_events(capacity_and_event_data)

        # Collect and process data based on Baymax's configuration
        # Collect devices counts from 'TrueSight Console -> Configuration -> Managed Devices'
        if baymax.isDevicesCountOn():
            response_json = ts_console.managed_devices(
                dp.get_console_url(), getattr(baymax, 'data'))
            if not type(response_json) == int:
                response_dict = json.loads(response_json)
                response = response_dict['response']
                devices_counts = (
                    str(response['dataCount']['isConnected']),
                    str(response['dataCount']['isDisconnected']),
                    str(response['dataCount']['agentConnected'] +
                        response['dataCount']['agentDisconnected']),
                    str(response['dataCount']['agentConnected']),
                    str(response['dataCount']['agentDisconnected'])
                )

                logging.info('Writing devices counts')
                pm.write_devices_counts(devices_counts)
                html_writer.devices_counts_html(devices_counts)

            else:
                logging.error('Response: HTTP %s', response_json)

        # Collect and process data based on Baymax's configuration
        # Collect devices counts from 'TrueSight Console -> Configuration -> Managed Devices'
        if baymax.isDisconnectedAgentsOn():
            response_json = ts_console.get_disconnected_agents(
                dp.get_console_url(), getattr(baymax, 'data'))
            if not type(response_json) == int:
                disconnected_agents_list = None
                response_data = json.loads(response_json)
                tsim = {}
                for tsim_server in response_data['response']['serverList']:
                    isns = {}
                    for integration_service in tsim_server['integrationServiceDetails']:
                        if not integration_service['isName'] == 'ProactiveServer':
                            agents = []
                            for patrol_agent in integration_service['patrolAgentDetails']:
                                agents.append(
                                    ':'.join([patrol_agent['hostname'], str(patrol_agent['agentPort'])]))
                            isns[integration_service['isName']] = agents
                    if bool(isns):
                        tsim[tsim_server['serverDNSName']] = isns
                disconnected_agents_list = tsim
                pm.write_disconnected_agents(disconnected_agents_list)
                html_writer.disconnected_agents_html(disconnected_agents_list)

    html_writer.close_html()

    # Postman sends email to all recipients listed in 'mail.json'
    postman = Postman(env, baymax)
    postman.compose()

    # Clean-up all files before sending email. Keep only HTML TSOM Usage & Devices Report.
    pm.cleanup()

    postman.send()
    logging.info('Bye')
