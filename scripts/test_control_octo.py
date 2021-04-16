import json

import requests


user_config_file = '../server/flaskr/config/user.json'
with open(user_config_file) as f:
    user_config = json.loads(f.read())


def octoprint_url(path):
    return f"http://{user_config['octoprint_ip_address']}/{path}"


class RunGCodeTest():
    aws_enabled = False

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': user_config['octoprint_api_key'],
            'Content-Type': 'application/json',
        })

    def homeAll(self):
        print("Homing all")
        return self.session.post(octoprint_url('api/printer/printhead/home'))

    def home(self, x=False, y=False, z=False):
        data = {
            'command': 'home',
            'axes': [],
        }
        if x: data['axes'].append('x')
        if y: data['axes'].append('y')
        if z: data['axes'].append('z')
        print(f"Homing: {data}")
        return self.session.post(octoprint_url('api/printer/printhead'), data=json.dumps(data))

    def moveToRelative(self, x=None, y=None, z=None):
        data = {'relative': True, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        print(data)
        return self.session.post(octoprint_url('api/printer/printhead'), data=json.dumps(data))

    def moveToAbsolute(self, x=None, y=None, z=None):
        data = {'absolute': True, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        print(data)
        return self.session.post(octoprint_url('api/printer/printhead'), data=json.dumps(data))

    def run(self):
        import pdb; pdb.set_trace()


if __name__ == '__main__':
    t = RunGCodeTest().run()
    import pdb; pdb.set_trace()
    # RunGCodeTest().run()
