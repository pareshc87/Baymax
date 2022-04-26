
import subprocess as sp
import os


class EventCellCLI:

    def __init__(self, env) -> None:
        self.env = env
        self.pw_home = '\\'.join([os.getcwd(), 'pw'])
        self.pw_bin = '\\'.join([self.pw_home, 'server', 'bin'])

    def event_cell_status(self, cell_name):
        return sp.run(['mcstat', '-n', cell_name], capture_output=True)
