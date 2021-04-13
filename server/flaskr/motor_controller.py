import serial
import time

from . import config

CONNECT_TIMEOUT = 5  # seconds
CONNECT_POLL_SLEEP = 5  # ms
CONNECT_POLL_ATTEMPTS = int((CONNECT_TIMEOUT * 1000) / CONNECT_POLL_SLEEP)


class MotorController(object):
    def __init__(self, port, baudrate, timeout):
        # this should probably be done on app init
        self.configure(port, baudrate, timeout)

    @classmethod
    def instance(cls):
        return _instance

    def configure(self, port=None, baudrate=None, timeout=None):
        print("Connecting to serial")
        # todo: automatically find port
        if port is not None:
            self.port = port
        if baudrate is not None:
            self.baudrate = baudrate
        if timeout is not None:
            self.timeout = timeout

        self._serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        # Serial does not open right away.. give it a little bit
        for i in range(CONNECT_POLL_ATTEMPTS):
            if self._serial.is_open:
                print(f" -- Connected to {self.port}")
                return True
            time.sleep(CONNECT_POLL_SLEEP)

        print(f" -- Failed to connect to {self.port}")
        return False


    def write_read(self, cmd):
        self._serial.write(bytes(cmd, 'utf-8'))
        time.sleep(0.05)
        response = []
        data = self._serial.readline()
        while data:
            data = self._serial.readline().decode('utf-8').strip();
            response.append(data)
        print(response)
        return response


_instance = MotorController(config.PORT_NAME, config.BAUD_RATE, config.SERIAL_TIMEOUT)
