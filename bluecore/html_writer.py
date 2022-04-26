
import os

from datetime import datetime
from time import strftime


class HTMLWriter:

    def __init__(self, environment) -> None:
        self.environment = environment
        self.today = datetime.now()
        report_name = ' '.join([
            'TSOM Usage & Devices Report',
            self.environment.upper(),
            self.today.strftime('%B %d, %Y')
        ])
        report_name = report_name + '.html'
        self.report_filename = '\\'.join([os.getcwd(), 'var', report_name])
        html = '''
        <html>
        <head>
         <title>Baymax</title>
         <style>
          body{
              font-family: 'Trebuchet MS', sans-serif;
          }
          h3{
              margin-bottom: 2px;
          }
          h4{
              margin-bottom: 8px;
          }
          #main{
              margin: 1% 8%;
          }
          .odd {
              background-color: #EEEEEE;
          }
          #capacity-metrics{
              border-collapse: collapse;
              width: 100%;
          }
          #capacity-metrics th, #capacity-metrics td{
              border: 1px solid #9E9E9E;
              padding: 4px 8px;
              text-align: center;
          }
          #capacity-metrics th{
              background-color: #FF9800;
          }
          #capacity-metrics{
              border-collapse: collapse;
              width: 100%;
          }
          #devices-counts{
              border-collapse: collapse;
              width: 100%;
          }
          #devices-counts th, #devices-counts td{
              border: 1px solid #9E9E9E;
              padding: 4px 8px;
              text-align: center;
          }
          #devices-counts th{
              background-color: #FF9800;
          }
          #devices-counts td{
              background-color: #EEEEEE;
          }
          #disconnected-agents{
              border-collapse: collapse;
              width: 100%;
          }
          #disconnected-agents th, #disconnected-agents td{
              border: 1px solid #9E9E9E;
              padding: 4px 8px;
          }
          #disconnected-agents th{
              background-color: #FF9800;
          }
          .tsim-server{
              background-color: #B0BEC5;
              text-align: center;
          }
          .isn{
              background-color: #ECEFF1;
              text-align: center;
          }
          .node {
              background-color: #F5F5F5;
          }
         </style>
        </head>
        <body>
         <div id='main'>
          <h3>TSOM Usage & Devices Report</h3>
        '''
        with open(self.report_filename, 'w') as fh:
            fh.write(html)

    def monitored_data_html(self, labels, tsim_servers, capacity_data):
        pronet_instance_large_max = 250000
        html = f'''
        <p style='margin-top: 2px;'>{self.today.strftime('%B %d, %Y')}</p>
        <div>
            <h4>Usage Summary</h4>
            <table id='capacity-metrics'>
                <tr><th style='text-align:left;'>Monitored Data</th>
        '''

        for tsim_server in tsim_servers:
            heading = tsim_server.replace('.pptparkview.com', '')
            html += f'''
            <th>{heading}</th>
            '''

        for i, label in enumerate(labels):
            if i % 2 == 0:
                html += f"<tr class='odd'><td style='text-align:left;'>{label}</td>"
            else:
                html += f"<tr><td style='text-align:left;'>{label}</td>"
            if not label == 'Monitor Instances':
                for col in range(len(capacity_data)):
                    html += f'''
                    <td>{capacity_data[col][i]}</td>
                    '''
            else:
                for col in range(len(capacity_data)):
                    html += f'''
                    <td>{capacity_data[col][i]} ({round(((int(capacity_data[col][i])/pronet_instance_large_max)*100), 2)}% Used)</td>
                    '''
            html += '</tr>'

        with open(self.report_filename, 'a') as fh:
            fh.write(html)

    def avg_events_per_day(self, avg_events):
        html = f'''
        <tr>
            <td style='text-align:left;'>All Events Average/day (5 days)</td>
        '''
        for num in avg_events:
            html += f'''
            <td>{num}</td>
            '''
        html += '</tr>'
        with open(self.report_filename, 'a') as fh:
            fh.write(html)

    def devices_counts_html(self, devices_counts):
        html = f'''
            </table>
        <p>pronet.instance.large.max = 250000</p>
        </div>
        <div>
            <h4>Device Counts</h4>
            <table id='devices-counts'>
                <tr>
                    <th>Connected Integration Services</th>
                    <th>Disconnected Integration Services</th>
                    <th>Total Agents Count</th>
                    <th>Connected Agents</th>
                    <th>Disconnected Agents</th>
                </tr>
                <tr>
                    <td>{devices_counts[0]}</td>
                    <td>{devices_counts[1]}</td>
                    <td>{devices_counts[2]}</td>
                    <td>{devices_counts[3]}</td>
                    <td>{devices_counts[4]}</td>
                </tr>
            </table>
        </div>
        '''
        with open(self.report_filename, 'a') as fh:
            fh.write(html)

    def disconnected_agents_html(self, agents: dict):

        html = '''
        <div>
            <h4>Disconnected Agents</h4>
            <table id='disconnected-agents'>
            <tr>
                <th>TSIM Server</th>
                <th>Integration Service</th>
                <th>Managed Node</th>
            </tr>
        '''

        tsim_rowspans = []
        for tsim, isns in agents.items():
            isn_rowspan = []
            for isn, nodes in isns.items():
                isn_rowspan.append(len(nodes))
            tsim_rowspans.append(sum(isn_rowspan))

        i = 0
        for tsim_server, isns in agents.items():
            current_tsim = None
            for isn, nodes in isns.items():
                current_isn = None
                for node in nodes:
                    html += '<tr>'
                    if not current_tsim == tsim_server:
                        current_tsim = tsim_server
                        html += f'''
                            <td class='tsim-server' rowspan={tsim_rowspans[i]}>
                            {tsim_server.replace('.pptparkview.com', '')}<br>
                            (Disconnected Agents={tsim_rowspans[i]})
                            </td>
                        '''
                    if not current_isn == isn:
                        current_isn = isn
                        html += f'''
                         <td class='isn' rowspan={len(nodes)}>{isn.replace('.pptparkview.local', '')}<br>
                         (Disconnected Agents={len(nodes)})
                         </td>
                        '''
                    html += f'''
                        <td class='node'>{node}</td></tr>
                    '''
            i += 1
        html += '''
                    </table>
                </div>
            '''
        with open(self.report_filename, 'a') as f:
            f.write(html)

    def close_html(self):
        html = '''
                    </div>
                    <div><p style='text-align: center;'>- End of Report -</p></div>
                </body>
            </html>
        '''

        with open(self.report_filename, 'a') as fh:
            fh.write(html)
