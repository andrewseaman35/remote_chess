import funcy
import json
import logging
import os

from .exceptions import InvalidConfigurationException

CONFIG_DIRECTORY = os.path.relpath(os.path.join('flaskr', 'config'))

DEFAULT_CONFIG_FILENAME = 'default.json'
USER_CONFIG_FILENAME = 'user.json'


logger = logging.getLogger(__name__)

"""
    "arduino_port": null,             # if null, attempt to detect port automatically, else use defined port
    "serial_timeout": 0.5,            # timeout for serial comms with arduino
    "serial_baudrate": 9600,          # baudrate for arduino
    "octoprint_api_key": "",          # octoprint api key
    "octoprint_ip_address": "",       # local ip of octopi instance
    "printer_stepper_timeout": 600,   # printer timeout to disable steppers (seconds)
    "printhead_x_offset": 0,          # (printer only), x offset between printer nozzle and hand center
                                      #    positive value means hand is in positive x direction (towards right) of head
    "printhead_z_offset": 100,        # (printer only), y offset between printer nozzle and hand center
                                      #    positive value means hand is in positive y direction (towards back) of head
    "z_axis_height": 50,              # (printer only), height of z axis
    "board_x_offset": 10,             # mm between left side of print bed and board
    "board_y_offset": 10,             # mm between front side of print bed and board
    "board_width": 210,               # x axis length of board in mm
    "board_depth": 210,               # y axis length of board in mm
    "space_width": 24,                # x axis length of space
    "space_depth": 24                 # y axis length of space
"""


class Configuration(object):
    # TODO: make this dict-like and save to user file
    def __init__(self):
        self.config_directory = os.path.abspath(CONFIG_DIRECTORY)
        if not os.path.exists(self.config_directory) or not os.path.isdir(self.config_directory):
            msg = f"config directory does not exist: {self.config_directory}"
            logger.error(msg)
            raise InvalidConfigurationException(msg)

        self.default_filepath = os.path.join(self.config_directory, DEFAULT_CONFIG_FILENAME)
        if not os.path.exists(self.default_filepath):
            msg = f"default config file does not exist: {self.default_filepath}"
            logger.error(msg)
            raise InvalidConfigurationException(msg)

        self.user_filepath = os.path.join(self.config_directory, USER_CONFIG_FILENAME)
        self.user_filepath_exists = True
        if not os.path.exists(self.user_filepath):
            msg = f"user config file does not exist: {self.user_filepath}"
            logger.warning(msg)
            self.user_filepath_exists = False

    @classmethod
    def config(self):
        return _instance

    # TODO: dict-like
    def get(self, key):
        return self._config[key]

    def _validate_config_value(self, key, value):
        if not key:
            raise InvalidConfigurationException('key cannot be null')
        if not value:
            raise InvalidConfigurationException('value cannot be null')
        if key not in self._default_config:
            raise InvalidConfigurationException('invalid configuration key')

    def set(self, key, value):
        self._validate_config_value(key, value)
        user_config = self._user_config.copy()
        user_config[key] = value
        with open(self.user_filepath, 'w') as f:
            f.write(json.dumps(user_config, sort_keys=True, indent=4))
        logger.info(f"config set: {key}={value}")

    @property
    def _default_config(self):
        with open(self.default_filepath) as f:
            return json.loads(f.read())

    @property
    def _user_config(self):
        if not self.user_filepath_exists:
            return {}
        try:
            with open(self.user_filepath) as f:
                return json.loads(f.read())
        except Exception as e:
            logger.warning("encountered error while loading user config")
            logger.warning(e)
            raise e
        return {}

    @property
    def _config(self):
        # TODO: cache this, using date modified timestamp of file as key?
        conf = self._default_config.copy()
        conf.update(self._user_config)
        return conf


_instance = Configuration()
