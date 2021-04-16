import json

import requests

from .config import Configuration


class AxisController(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': Configuration.config().get('octoprint_api_key'),
            'Content-Type': 'application/json',
        })

    @classmethod
    def instance(cls):
        return _instance

    def octoprint_url(self, path):
        return f"http://{Configuration.config().get('octoprint_ip_address')}/{path}"

    @property
    def printhead_url(self):
        return self.octoprint_url(f"api/printer/printhead")

    def home(self, x=False, y=False, z=False):
        axes = []
        if x: axes.append('x')
        if y: axes.append('y')
        if z: axes.append('z')
        return self.session.post(self.printhead_url, data=json.dumps({
            'command': 'home',
            'axes': axes,
        }))

    def move_to_relative(self, x=None, y=None, z=None):
        data = {'absolute': False, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        print(data)
        return self.session.post(self.printhead_url, data=json.dumps(data))

    def move_to_absolute(self, x=None, y=None, z=None):
        data = {'absolute': True, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        print(data)
        return self.session.post(self.printhead_url, data=json.dumps(data))


_instance = AxisController()
