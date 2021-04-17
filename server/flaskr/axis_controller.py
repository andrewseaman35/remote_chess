import json
import logging
import re

import funcy
import requests

from .config import Configuration

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
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': Configuration.config().get('octoprint_api_key'),
            'Content-Type': 'application/json',
        })
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

    def _calculate_x_from_file(self, file):
        file_index = file_to_index(file)
        printer_profile = self.printer_profile()
        width = printer_profile['volume']['width']

        config = Configuration.config()
        board_x_offset = config.get('board_x_offset')
        board_x_padding = ((config.get('board_width') - (config.get('space_width') * NUM_FILES)) / 2)
        board_left_edge = board_x_offset + board_x_padding
        space_edge = board_left_edge + int(config.get('space_width') * file_index)
        return space_edge + (config.get('space_width') / 2)

    def _calculate_y_from_rank(self, rank):
        rank_index = rank_to_index(rank)
        printer_profile = self.printer_profile()
        depth = printer_profile['volume']['depth']

        config = Configuration.config()
        board_y_offset = config.get('board_y_offset')
        board_y_padding = ((config.get('board_depth') - (config.get('space_depth') * NUM_RANKS)) / 2)
        board_far_edge = board_y_offset + board_y_padding
        space_edge = board_far_edge + int(config.get('space_depth') * rank_index)

        final_shift = space_edge + (config.get('space_depth') / 2)
        return final_shift

    @funcy.memoize
    def printer_profile(self, profile_id=PRINTER_PROFILE_DEFAULT_ID):
        response = self.session.get(f"{self.printer_profiles_url}/{profile_id}")
        if not response.ok:
            raise Exception('something')
        response_json = json.loads(response.content)
        return response_json

    def home(self, x=False, y=False, z=False):
        axes = []
        if x: axes.append('x')
        if y: axes.append('y')
        if z: axes.append('z')
        logger.info(f"Homing {axes}")
        response = self.session.post(self.printhead_url, data=json.dumps({
            'command': 'home',
            'axes': axes,
        }))
        logger.info(response.ok)
        if response.ok:
            if x: self.homed['x'] = True
            if y: self.homed['y'] = True
            if z: self.homed['z'] = True
            return 'done'
        return 'dang'

    def move_to_relative(self, x=None, y=None, z=None):
        data = {'absolute': False, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        data['speed'] = 1000
        logger.info(data)
        return self.session.post(self.printhead_url, data=json.dumps(data))

    def move_to_space(self, space):
        if not (self.homed['x'] and self.homed['y']):
            raise Exception("must home x and y first")

        data = {'absolute': True, 'command': 'job'}
        parsed_space = parse_space_position(space)
        data = {
            'x': self._calculate_x_from_file(parsed_space['file']),
            'y': self._calculate_y_from_rank(parsed_space['rank']),
            'z': 50,
        }
        return self.move_to_absolute(**data)

    def move_to_absolute(self, x=None, y=None, z=None):
        if not self.has_been_homed:
            raise Exception('not homed, homie')
        data = {'absolute': True, 'command': "jog"}
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        data['speed'] = 1000
        print(data)
        return self.session.post(self.printhead_url, data=json.dumps(data))


_instance = AxisController()
