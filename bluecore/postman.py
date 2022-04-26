
import os
import json
import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from bs4 import BeautifulSoup
from .data_provider import DataProvider
from .persistence_manager import PersistenceManager


class Postman:

    def __init__(self, env, baymax) -> None:
        self.env = env
        self.baymax = baymax
        self.config = getattr(self.baymax, 'config')
        self.today = datetime.now()

        with open(os.path.join(os.getcwd(), 'mail.json'), 'r') as fh:
            self.mail_config = json.load(fh)

    def compose(self):
        # Instantiate DataProvider to fetch data from 'environment.json'
        dp = DataProvider(self.env)
        # Instantiate PersistenceManager to fetch collected data
        pm = PersistenceManager(self.env)

        # Compose Capacity Summary in email if enabled in 'configuration.json'
        if self.baymax.isCapacityMetricsOn():
            tsim_servers = dp.get_servers()

            # Compose Capacity Summary Header
            capacity_summary_header = [
                ''.join([
                    '<td style="padding-left: 10px;padding-right: 10px;">',
                    tsim_server,
                    '</td>']) for tsim_server in tsim_servers
            ]
            capacity_summary_header.insert(0, '''<tr bgcolor="#f39c12" style="color: white;">
                <td style="padding-left: 10px;padding-right: 10px;">Metric</td>''')
            capacity_summary_header.append('</tr>')
            capacity_summary_header = ''.join(capacity_summary_header)

            keys = self.config['performance_diagnostics']['keys']
            if self.baymax.isGetMaxAlarmDetailsOn():
                keys.append('Avg. events/day (5 days)')
            capacity_summary_data = pm.read_monitored_data_and_events()

            # Compose Capacity Summary Body
            capacity_summary_body = []
            for i in range(len(keys)):
                if i % 2 != 0:
                    capacity_summary_body.append(
                        f'<tr bgcolor="#f2f3f4"><td style="padding-left: 10px;padding-right: 10px;">{keys[i]}</td>')
                else:
                    capacity_summary_body.append(
                        f'<tr><td style="padding-left: 10px;padding-right: 10px;">{keys[i]}</td>')
                capacity_summary_body += [
                    f'<td style="text-align: center;padding-left: 10px;padding-right: 10px;">{row[i]}</td>'
                    for row in capacity_summary_data]
                capacity_summary_body.append('</tr>')

            capacity_summary_body = ''.join(capacity_summary_body)

            # Add percent utilized in monitor instances row
            soup = BeautifulSoup(capacity_summary_body, features='html.parser')
            rows = soup.find_all('tr')
            monitor_instances_row = rows[1]
            cols = monitor_instances_row.find_all('td')
            for col in cols[1::]:
                original_val = int(col.string)
                percent_utilized = round(
                    ((original_val / dp.get_pronet_instance_max())*100), 2)
                col.append(f' ({percent_utilized}% Used)')

            capacity_summary_body = soup

            # Compose Capacity Summary to mail
            capacity_summary = f"""
                <div class='monitored_data'>
                    <h4>Capacity Summary</h4>
                    <table>
                        <thead>{capacity_summary_header}</thead>
                        <tbody>{capacity_summary_body}</tbody>
                    </table>
                    <div>
                        <p>pronet.instance.large.max = 250000</p>
                    </div>
                </div>
            """
        else:
            capacity_summary = '<div><p>Capacity Summary: Disabled</p></div>'

        # Compose Devices Summary in email if enabled in 'configuration.json'
        if self.baymax.isDevicesCountOn():
            labels = [
                "Connected Integration Services",
                "Disconnected Integration Services",
                "Total PATROL Agents",
                "Connected Agents",
                "Disconneted Agents",
            ]

            # Compose Devices Summary Header
            devices_summary_header = [
                f'<td style="padding-left: 10px;padding-right: 10px;">{label}</td>'
                for label in labels]
            devices_summary_header.insert(
                0, '<tr bgcolor="#f39c12 " style="color: white;">')
            devices_summary_header.append('</tr>')
            devices_summary_header = ''.join(devices_summary_header)

            # Fetch devices counts from files
            devices_counts = pm.read_devices_counts()
            # Compose Devices Summary Body
            devices_summary_body = [
                f'<td bgcolor="#f2f3f4" style="text-align: center;padding-left: 10px;padding-right: 10px;">{value}</td>'
                for value in devices_counts[0]]
            devices_summary_body.insert(0, '<tr>')
            devices_summary_body.append('</tr>')
            devices_summary_body = "".join(devices_summary_body)

            # Compose Devices Summary to mail
            devices_summary = f"""
                <div class='devices_counts'>
                    <h4>Devices Summary</h4>
                    <table>
                        <thead>{devices_summary_header}</thead>
                        <tbody>{devices_summary_body}</tbody>
                    </table>
                </div>
            """
        else:
            devices_summary = '<div><p>Devices Summary: Disabled<p></div>'

        self.mail = f"""
            <html>
            <head></head>
            <body>
                <div id='main'>
                    {capacity_summary}
                    {devices_summary}
                    <div>
                        <p><b>To view detailed report, use Google Chrome or Mozilla Firefox to open attached HTML Report.</b></p>
                        <p>This is an auto-generated email, please do not reply.</p>
                        <p><b>Thanks & Regards,</b><br/><i>Baymax</i></p>
                    </div>
                </div>
            </body>
            </html>
        """

        self.msg = MIMEMultipart('alternative')
        self.msg['subject'] = ' '.join([
            self.mail_config['subject'],
            self.env.upper(),
            datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        ])
        self.msg['from'] = self.mail_config['from']
        self.msg['to'] = ','.join(self.mail_config[self.env]['to'])
        if 'cc' in self.mail_config[self.env].keys():
            self.msg['cc'] = ','.join(self.mail_config[self.env]['cc'])
        self.msg.attach(MIMEText(self.mail, 'html'))

        # Attach TSOM Usage & Devices Report <env>.html
        report_name = ' '.join([
            'TSOM Usage & Devices Report',
            self.env.upper(),
            self.today.strftime('%B %d, %Y')
        ])
        report_filename = report_name + '.html'
        report = MIMEBase('application', 'octet-stream')
        report.set_payload(open('\\'.join([os.getcwd(), 'var', report_filename]), 'rb').read())
        encoders.encode_base64(report)
        report.add_header('Content-Disposition', f'attachment; filename="{report_filename}"')
        self.msg.attach(report)

    def send(self):
        to = self.mail_config[self.env]['to']
        if 'cc' in self.mail_config[self.env].keys():
            cc = self.mail_config[self.env]['cc']
            recipients = to + cc
        else:
            recipients = to
        with smtplib.SMTP(host="pptm-sys-util.pptparkview.local", port=25) as sm:
            sm.sendmail(self.mail_config['from'],
                        recipients, self.msg.as_string())
            logging.info("Email sent!")
