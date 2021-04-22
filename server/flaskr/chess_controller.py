from flask import current_app
import time

from .axis_controller import AxisController
from .motor_controller import MotorController

class ChessController(object):
    @classmethod
    def instance(cls):
        return _instance

    def perform_move(self, starting_space, ending_space, skip_hand=False):
        # assume that we start above the pieces
        axis_controller = AxisController.instance()
        motor_controller = current_app.motor_controller
        axis_controller.move_to_space(starting_space)
        time.sleep(5)  # Let's just make this more than it'll ever be
        if not skip_hand:
            motor_controller.z_down()
            time.sleep(5)
            motor_controller.hand_close()
            time.sleep(3)
            motor_controller.z_up()
            time.sleep(5)
        axis_controller.move_to_space(ending_space)
        time.sleep(5)
        if not skip_hand:
            motor_controller.z_down()
            time.sleep(5)
            motor_controller.hand_open()
            time.sleep(3)
            motor_controller.z_up()

    def perform_moves(self, moves, skip_hand=False):
        for (starting_space, ending_space) in moves:
            self.perform_move(starting_space, ending_space, skip_hand=skip_hand)


_instance = ChessController()
