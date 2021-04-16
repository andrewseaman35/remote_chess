from flask import (Blueprint, render_template, request, Response, jsonify)

from .motor_controller import MotorController


bp = Blueprint('base', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')


@bp.route('/status', methods=['GET'])
def status_ajax():
    # complete status endpoint for now. This should get broken up into more specific endpoints if necessary.
    instance = MotorController.instance()
    return jsonify({
        'motor_controller': {
            'port': instance.port,
            'baudrate': instance.baudrate,
            'timeout': instance.timeout,
        },
    })
