from flask import (Blueprint, render_template, request, Response, jsonify)

from .motor_controller import MotorController

bp = Blueprint('chess_v1', __name__, url_prefix='/chess_v1')

@bp.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test_page.html')


@bp.route('/raw_write', methods=['POST'])
def raw_write():
    json_data = request.get_json()
    response = MotorController.instance().write_read(json_data['command'])
    return jsonify({'data': response})
