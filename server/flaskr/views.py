from flask import (Blueprint, render_template, request, Response, jsonify)
from flask_cors import cross_origin
from werkzeug.exceptions import BadRequest

from .config import Configuration
from .exceptions import InvalidConfigurationException
from .motor_controller import MotorController


bp = Blueprint('base', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')


@bp.route('/status', methods=['GET'])
@cross_origin()
def status():
    # complete status endpoint for now. This should get broken up into more specific endpoints if necessary.
    instance = MotorController.instance()
    return jsonify({
        'status': 'OK',
        'axis_controller': {

        },
        'motor_controller': {
            'configuration': {
                'port': instance.port,
                'baudrate': instance.baudrate,
                'timeout': instance.timeout,
            }
        },
    })


@bp.route('/configure', methods=['GET', 'PATCH'])
@cross_origin()
def configure():
    config = Configuration.config()
    if request.method == 'GET':
        return jsonify(config._config)
    else:
        json_data = request.json
        key = json_data.get('key')
        value = json_data.get('value')
        try:
            config.set(key, value)
        except InvalidConfigurationException as e:
            raise BadRequest(str(e))
        return '', 204

