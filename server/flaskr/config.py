import functools
import json
import logging
import os

CONFIG_DIRECTORY = os.path.relpath(os.path.join('flaskr', 'config'))

DEFAULT_CONFIG_FILENAME = 'default.json'
USER_CONFIG_FILENAME = 'user.json'


logger = logging.getLogger(__name__)


class Configuration(object):
    # TODO: make this dict-like and save to user file
    def __init__(self):
        self.config_directory = os.path.abspath(CONFIG_DIRECTORY)
        if not os.path.exists(self.config_directory) or not os.path.isdir(self.config_directory):
            msg = f"config directory does not exist: {self.config_directory}"
            logger.error(msg)
            raise Exception(msg)

        self.default_filepath = os.path.join(self.config_directory, DEFAULT_CONFIG_FILENAME)
        if not os.path.exists(self.default_filepath):
            msg = f"default config file does not exist: {self.default_filepath}"
            logger.error(msg)
            raise Exception(msg)

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
        return {}

    @property
    def _config(self):
        # TODO: cache this, using date modified timestamp of file as key?
        conf = self._default_config.copy()
        conf.update(self._user_config)
        return conf


_instance = Configuration()
