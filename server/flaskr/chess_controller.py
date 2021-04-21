import time

from .axis_controller import AxisController
from .motor_controller import MotorController

class ChessController(object):
    @classmethod
    def instance(cls):
        return _instance

    def move_piece(self, starting_space, ending_space):
        # assume that we start above the pieces
        axis_controller = AxisController.instance()
        motor_controller = MotorController.instance()
        axis_controller.move_to_space(starting_space)
        time.sleep(5)  # Let's just make this more than it'll ever be
        # motor_controller.hand_open()
        # time.sleep(5)  # Let's time this and see what it's usually
        motor_controller.z_down()
        time.sleep(5)
        motor_controller.hand_close()
        time.sleep(3)
        motor_controller.z_up()
        time.sleep(5)
        axis_controller.move_to_space(ending_space)
        time.sleep(5)
        motor_controller.z_down()
        time.sleep(5)
        motor_controller.hand_open()
        time.sleep(3)
        motor_controller.z_up()


_instance = ChessController()
