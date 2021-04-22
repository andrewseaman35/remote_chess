from flask import (
    current_app,
    Blueprint,
    render_template,
    request,
    Response,
    jsonify,
)
from flask_cors import cross_origin
from werkzeug.exceptions import BadRequest

from .exceptions import AxisControllerException, MotorControllerException

from .axis_controller import AxisController
from .chess_controller import ChessController


bp = Blueprint('chess_v1', __name__, url_prefix='/chess_v1')

@bp.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test_page.html')


@bp.route('/raw_write', methods=['POST'])
def raw_write():
    json_data = request.get_json()
    response = current_app.motor_controller.write_read(json_data['command'])
    return jsonify({'data': response})


@bp.route('/printer_action_test', methods=['POST'])
def test_printer_action():
    json_data = request.get_json()
    action = json_data['action']
    controller = current_app.axis_controller
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


@bp.route('/octoprint_status', methods=['GET'])
@cross_origin()
def octoprint_status():
    status = current_app.axis_controller.get_octoprint_server_status()
    return jsonify(status)


@bp.route('/initialize_octoprint', methods=['GET'])
@cross_origin()
def intialize_octoprint():
    initialized, message = current_app.axis_controller.intialize_octoprint()
    if initialized:
        return '', 204
    raise BadRequest(response.reason)


@bp.route('/initialize_controller', methods=['GET'])
@cross_origin()
def initialize_controller():
    initialized, message = current_app.motor_controller.initialize()
    if initialized:
        return '', 204
    raise BadRequest(response.reason)


@bp.route('/controller_serial_status', methods=['GET'])
@cross_origin()
def controller_serial_status():
    try:
        status = current_app.motor_controller.get_controller_serial_status()
    except MotorControllerException as e:
        raise BadRequest(e)
    return jsonify(status)


@bp.route('/home_axes', methods=['GET'])
@cross_origin()
def home_axes():
    current_app.axis_controller.home(x=True, y=True, z=True, use_hand_offset=True)
    return '', 204


@bp.route('/perform_moves', methods=['POST'])
@cross_origin()
def perform_moves():
    # change to a list of dicts with {action: [move|capture], startingSpace: B3, endingSpace: A1}
    json_data = request.get_json()
    try:
        response = ChessController.instance().perform_moves(
            moves=json_data['moves'],
            skip_hand=True,
        );
    except AxisControllerException as e:
        raise BadRequest(e)
    return '', 204
