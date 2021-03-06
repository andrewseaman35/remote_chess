import json
import logging
import re

import funcy
import requests

from .config import Configuration
from .exceptions import AxisControllerException, OctoPrintException

PRINTER_PROFILE_DEFAULT_ID = '_default'  # set by OctoPrint

NUM_RANKS = 8
NUM_FILES = 8

space_position_regex = re.compile(r'(?P<file>[A-Z])(?P<rank>[0-9]+)')
spr = re.compile(r'(?P<file>[A-Z])(?P<rank>[0-9]+)')

logger = logging.getLogger(__name__)


def parse_space_position(position):
    match = space_position_regex.match(position)
    if not match:
        raise Exception(f"invalid space position: {position}")
    groups = match.groupdict()
    return {
        'rank': int(groups['rank']),
        'file': groups['file'].upper(),
    }


def rank_to_index(rank):
    logger.info(rank)
    if not (1 <= rank <= 8):
        raise Exception(f"bad rank: {rank}")
    return rank - 1


def file_to_index(file):
    if file not in {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'}:
        raise Exception(f"bad file: {file}")
    return int(ord(file) - 65)


class AxisController(object):
    def __init__(self):
        self._initialized = False
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': Configuration.config().get('octoprint_api_key'),
            'Content-Type': 'application/json',
        })

        try:
            int(Configuration.config().get('z_axis_height'))
        except ValueError:
            raise Exception('need valid config value for z_axis_height')

        self.homed = {
            'x': False,
            'y': False,
            'z': False,
        }

    @classmethod
    def instance(cls):
        return _instance

    def octoprint_url(self, path):
        return f"http://{Configuration.config().get('octoprint_ip_address')}/{path}"

    @property
    def printhead_url(self):
        return self.octoprint_url(f"api/printer/printhead")

    @property
    def printer_profiles_url(self):
        return self.octoprint_url(f"api/printerprofiles")

    @property
    def has_been_homed(self):
        return self.homed['x'] and self.homed['y'] and self.homed['z']

    # START Initialization methods #
    def intialize_octoprint(self):
        # this is only really necessary for testing on the Ender since the z axis can slide down
        # if the steppers are disabled
        config = Configuration.config()
        logger.info("starting OctoPrint initialization")
        response = self.session.post(
            self.octoprint_url("/api/printer/command"),
            data=json.dumps({
                'commands': [
                    f"M84 S{config.get('printer_stepper_timeout')}",  # set stepper timeout
                    "M107",  # disable extruder fan
                ]
            })
        )
        if response.ok:
            logger.info("OctoPrint initialization complete")
            self._initialized = True
            return True, ''

        logger.info(f"OctoPrint initialization failed: {response.status_code}, {response.reason}")
        return False, response.reason

    def get_octoprint_server_status(self):
        logger.info("getting OctoPrint server status")
        checks = {
            'initialized': self._initialized,
            'version': {
                'status': 'NOT OK',
                'message': '',
            },
            'connection': {
                'status': 'NOT OK',
                'message': '',
            },
            'job': {
                'status': 'NOT OK',
                'message': '',
            }
        }
        config = Configuration.config()

        def not_ok_message(response, check):
            return f"received {response.status_code}, {response.reason} checking OctoPrint {check}"

        logger.info("checking OctoPrint version")
        try:
            version_response = self.session.get(self.octoprint_url('/api/version'), timeout=10)
        except requests.exceptions.ConnectionError:
            logger.error(f"ConnectionError encountered connectinng to octoprint")
            checks['version']['status'] = 'NOT OK'
            checks['version']['message'] = 'failed to connect, is OctoPrint running?'
            return checks

        if version_response.ok:
            logger.info("version check OK")
            checks['version']['status'] = 'OK'
        else:
            logger.error(f"version check failed with status {version_response.status_code} {version_response.reason}")
            checks['version']['status'] = 'NOT OK'
            checks['version']['message'] = not_ok_message(version_response, 'version')
            return checks

        logger.info("checking OctoPrint connection")
        connection_response = self.session.get(self.octoprint_url('/api/connection'))
        if connection_response.ok:
            connection_status = connection_response.json()['current']['state']
            is_operational = connection_status == 'Operational'
            if is_operational:
                logger.info("connection check OK")
                checks['connection']['status'] = 'OK'
            else:
                logger.error(f"connection check failed, non-operational status {connection_status}")
                checks['connection']['status'] = 'NOT OK'
                checks['connection']['message'] = f"received non-operational state {connection_status}"
        else:
            logger.error(f"connection check failed with status {connection_response.status_code} {connection_response.reason}")
            checks['connection']['status'] = 'NOT OK'
            checks['connection']['message'] = not_ok_message(connection_response, 'connection')
            return checks

        logger.info("checking OctoPrint job status")
        job_response = self.session.get(self.octoprint_url('/api/job'))
        if job_response.ok:
            job_status = job_response.json()['state']
            is_operational = job_status == 'Operational'
            if is_operational:
                logger.info("job check OK")
                checks['job']['status'] = 'OK'
                checks['job']['message'] = ''
            else:
                logger.error(f"job check failed, non-operational status {job_status}")
                checks['job']['status'] = 'NOT OK'
                checks['job']['message'] = f"received non-operational state {job_status}"
        else:
            logger.error(f"job check failed with status {job_response.status_code} {job_response.reason}")
            checks['job']['status'] = 'NOT OK'
            checks['job']['message'] = not_ok_message(job_response, 'job')

        logger.info("OctoPrint server status check complete")
        return checks

    # END Initialization methods #

    def _calculate_x_from_file(self, file):
        file_index = file_to_index(file)
        printer_profile = self.printer_profile()
        width = printer_profile['volume']['width']

        config = Configuration.config()
        board_x_offset = config.get('board_x_offset')
        board_x_padding = config.get('board_x_padding')
        board_left_edge = board_x_offset + board_x_padding
        space_edge = board_left_edge + int(config.get('space_width') * file_index)
        space_center = space_edge + (config.get('space_width') / 2)
        x_position = space_center - config.get('printhead_x_offset')
        return x_position

    def _calculate_y_from_rank(self, rank):
        rank_index = rank_to_index(rank)

        config = Configuration.config()
        board_y_offset = config.get('board_y_offset')
        board_y_padding = config.get('board_y_padding')
        board_near_edge = board_y_offset + board_y_padding
        space_edge = board_near_edge + int(config.get('space_depth') * rank_index)

        space_center = space_edge + (config.get('space_depth') / 2)
        y_position = space_center - config.get('printhead_y_offset')
        return y_position

    @funcy.memoize
    def printer_profile(self, profile_id=PRINTER_PROFILE_DEFAULT_ID):
        response = self.session.get(f"{self.printer_profiles_url}/{profile_id}")
        if not response.ok:
            raise OctoPrintException(f"get printer profile failed with status {response.status_code} {response.reason}")

        return json.loads(response.content)

    def home(self, x=False, y=False, z=False, use_hand_offset=False):
        axes = []
        if x: axes.append('x')
        if y: axes.append('y')
        if z: axes.append('z')
        logger.info(f"Homing {axes}")
        response = self.session.post(self.printhead_url, data=json.dumps({
            'command': 'home',
            'axes': axes,
        }))
        if response.ok:
            if x: self.homed['x'] = True
            if y: self.homed['y'] = True
            if z: self.homed['z'] = True
            logger.info("homing complete")
            if use_hand_offset:
                self.move_to_relative(x=0, y=0, z=Configuration.config().get('z_axis_height'))
            return
        logger.error(f"homing failed with status {response.status_code} {response.reason}")
        raise OctoPrintException(f"homing failed with status {response.status_code} {response.reason}")

    def move_to_relative(self, x=None, y=None, z=None):
        logger.info(f"moving to relative position: ({x}, {y}, {z})")
        if not self._initialized:
            raise AxisControllerException("axis controller not initialized")

        data = {'absolute': False, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        data['speed'] = Configuration.config().get('printhead_speed')
        logger.info(data)

        response = self.session.post(self.printhead_url, data=json.dumps(data))
        if not response.ok:
            raise OctoPrintException(f"moving relative failed with status {response.status_code} {response.reason}")

    def move_to_space(self, space):
        logger.info(f"moving to space: ({space})")
        data = {'absolute': True, 'command': 'job'}
        parsed_space = parse_space_position(space)
        data = {
            'x': self._calculate_x_from_file(parsed_space['file']),
            'y': self._calculate_y_from_rank(parsed_space['rank']),
            'z': Configuration.config().get('z_axis_height'),
        }
        return self.move_to_absolute(**data)

    def move_to_absolute(self, x=None, y=None, z=None):
        logger.info(f"moving to absolute position: ({x}, {y}, {z})")
        if not self._initialized:
            raise AxisControllerException("axis controller not initialized")
        if not self.has_been_homed:
            raise AxisControllerException("home axes first")

        data = {'absolute': True, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        data['speed'] = Configuration.config().get('printhead_speed')
        logger.info(data)

        # I think we'll have to calculate how long we think this will take and wait that long -__-
        # No support for polling position through octoprint and arbitrary commands return 204 no content
        # So that means we'll have to keep track of current position? Oof, maybe we can just wait longer than
        # we'll always need, since this is a proof of concept and all...
        response = self.session.post(self.printhead_url, data=json.dumps(data))
        if not response.ok:
            raise OctoPrintException(f"moving relative failed with status {response.status_code} {response.reason}")


_instance = AxisController()
