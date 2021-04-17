from flask import (Blueprint, render_template, request, Response, jsonify)

from .motor_controller import MotorController
from .axis_controller import AxisController
from .chess_controller import ChessController

bp = Blueprint('chess_v1', __name__, url_prefix='/chess_v1')

@bp.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test_page.html')


@bp.route('/raw_write', methods=['POST'])
def raw_write():
    json_data = request.get_json()
    response = MotorController.instance().write_read(json_data['command'])
    return jsonify({'data': response})


@bp.route('/printer_action_test', methods=['POST'])
def test_printer_action():
    json_data = request.get_json()
    action = json_data['action']
    controller = AxisController.instance()
    if action == 'homeXY':
        response = controller.home(x=True, y=True)
    elif action == 'homeZ':
        response = controller.home(z=True)
    elif action == 'relativeMove':
        params = {
            'x': int(json_data['x']),
            'y': int(json_data['y']),
            'z': int(json_data['z']),
        }
        response = controller.move_to_relative(**params)
    elif action == 'absoluteMove':
        params = {
            'x': int(json_data['x']),
            'y': int(json_data['y']),
            'z': int(json_data['z']),
        }
        response = controller.move_to_absolute(**params)
    elif action == 'moveToSpace':
        params = {
            'space': json_data['space']
        }
        response = controller.move_to_space(**params)
        return jsonify(response)
    elif action == 'movePiece':
        response = ChessController.instance().move_piece(json_data['starting_space'], json_data['ending_space'])
        return jsonify(response)
    else:
        response = Response(f"invalid action {action}", status_code=400)

    return response
