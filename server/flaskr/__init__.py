import os
import logging
import sys

from flask import Flask

from .motor_controller import MotorController
from .config import Configuration


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # configure logging
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import views
    app.register_blueprint(views.bp)

    from . import chess_v1
    app.register_blueprint(chess_v1.bp)

    # TODO: make this async
    MotorController.instance().configure(
        baudrate=Configuration.config().get('serial_baudrate'),
        timeout=Configuration.config().get('serial_timeout'),
    )

    logging.info("App initialization complete")

    return app
