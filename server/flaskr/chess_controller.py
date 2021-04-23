from flask import current_app
import time

from .axis_controller import AxisController
from .motor_controller import MotorController

class ChessController(object):
    @classmethod
    def instance(cls):
        return _instance

    def perform_move_to_space(self, starting_space, ending_space, skip_hand=False):
        # assume that we start above the pieces
        axis_controller = current_app.axis_controller
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

    def perform_remove_from_board(self, space, skip_hand=False):
        # TODO ??
        # maybe just drop it off the side of the board? lol
        axis_controller = current_app.axis_controller
        motor_controller = current_app.motor_controller
        axis_controller.move_to_space(space)
        time.sleep(5)  # Let's just make this more than it'll ever be
        if not skip_hand:
            motor_controller.z_down()
            time.sleep(5)
            motor_controller.hand_close()
            time.sleep(3)
            motor_controller.z_up()
            time.sleep(5)
        discard_space = 'A4'  # TODO: find somewhere off the board to drop the piece
        axis_controller.move_to_space(discard_space)
        time.sleep(5)
        if not skip_hand:
            motor_controller.hand_open()
            time.sleep(3)

    def perform_moves(self, moves, skip_hand=True):
        for move in moves:
            action = move['action']
            if action == 'move_to_space':
                self.perform_move_to_space(
                    move['starting_space'],
                    move['ending_space'],
                    skip_hand=skip_hand,
                )
            elif action == 'remove_from_board':
                self.perform_remove_from_board(
                    move['space'],
                    skip_hand=skip_hand,
                )


_instance = ChessController()
