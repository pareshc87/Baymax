
import os
import csv
import logging
import json


from datetime import date, datetime


class PersistenceManager:

    def __init__(self, env) -> None:
        if not os.path.isdir(os.path.join(os.getcwd(), 'var')):
            os.mkdir('.\\var')
        self.env = env
        self.save_date = datetime.now().strftime("%m%d%Y")
        # Filenames for storage
        self.devices_counts_filename = os.getcwd(
        ) + '_'.join([f'\\var\\{self.env}_devices', self.save_date]) + '.csv'
        self.disconnected_agents_filename = os.getcwd(
        ) + '_'.join([f'\\var\\{self.env}_disconnected_agents', self.save_date]) + '.json'
        self.monitored_data_filename = os.getcwd(
        ) + '_'.join([f'\\var\\{self.env}_capacity', self.save_date]) + '.csv'
        self.event_per_day_filename = os.getcwd(
        ) + '_'.join([f'\\var\\{self.env}_events_per_day', self.save_date]) + '.csv'
        self.combined_metrics_filename = os.getcwd(
        ) + '_'.join([f'\\var\\{self.env}_capacity+events', self.save_date]) + '.csv'

    def write_devices_counts(self, devices_counts):
        data = ','.join(devices_counts)
        with open(self.devices_counts_filename, 'w') as fh:
            fh.write(data)
            fh.write('\n')
        logging.info("Devices count stored in %s",
                     self.devices_counts_filename)

    def write_disconnected_agents(self, disconnected_agents):
        with open(self.disconnected_agents_filename, 'w') as fh:
            json.dump(disconnected_agents, fh)
        logging.info("Disconnected agents list stored in %s",
                     self.disconnected_agents_filename)

    def read_devices_counts(self):
        data = []
        with open(self.devices_counts_filename, 'r') as fh:
            rows = csv.reader(fh, delimiter=',')
            data = [row for row in rows]
        return data

    def write_monitored_data(self, monitored_data):
        with open(self.monitored_data_filename, 'w') as fh:
            for data in monitored_data:
                fh.write(','.join(data))
                fh.write('\n')
        logging.info("Monitored data stored in %s",
                     self.monitored_data_filename)

    def write_avg_events_day_5_days(self, events_per_day_list):
        with open(self.event_per_day_filename, 'w') as fh:
            for eventPerDay in events_per_day_list:
                fh.write(eventPerDay)
                fh.write('\n')
        logging.info("Average events/day for 5 days (internal & external) stored in %s",
                     self.event_per_day_filename)

    def write_monitored_data_and_events(self, data):
        with open(self.combined_metrics_filename, 'w') as fh:
            for capacity_metric in data:
                fh.write(','.join(capacity_metric))
                fh.write('\n')
        logging.info("Monitored data & Average events/day for 5 days (internal & external) stored in %s",
                     self.combined_metrics_filename)

    def read_monitored_data_and_events(self):
        data = []
        with open(self.combined_metrics_filename, 'r') as fh:
            rows = csv.reader(fh, delimiter=',')
            data = [row for row in rows]
        return data

    def cleanup(self):
        if os.path.isfile(self.monitored_data_filename):
            os.remove(self.monitored_data_filename)
        if os.path.isfile(self.event_per_day_filename):
            os.remove(self.event_per_day_filename)
        if os.path.isfile(self.combined_metrics_filename):
            os.remove(self.combined_metrics_filename)
        if os.path.isfile(self.devices_counts_filename):
            os.remove(self.devices_counts_filename)
        if os.path.isfile(self.disconnected_agents_filename):
            os.remove(self.disconnected_agents_filename)
