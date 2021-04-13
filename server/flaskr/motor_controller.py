import serial
import time

from . import config


class MotorController(object):
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self._arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    @classmethod
    def instance(cls):
        return _instance

    def write_read(self, cmd):
        self._arduino.write(bytes(cmd, 'utf-8'))
        time.sleep(0.05)
        response = []
        data = self._arduino.readline()
        while data:
            response.append(data.decode('utf-8').strip())
            data = self._arduino.readline();

        return response


_instance = MotorController(config.PORT_NAME, config.BAUD_RATE, config.SERIAL_TIMEOUT)
