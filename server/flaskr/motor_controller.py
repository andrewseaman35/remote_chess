import serial
import time
import sys
import glob
import logging

from .config import Configuration
from .exceptions import MotorControllerException

CONNECT_TIMEOUT = 5  # seconds
CONNECT_POLL_SLEEP = 0.05  # seconds
CONNECT_POLL_ATTEMPTS = int(CONNECT_TIMEOUT / CONNECT_POLL_SLEEP)

HANDSHAKE = 'heybuddy'
HANDSHAKE_ACK = 'eyyy'
HANDSHAKE_TIMEOUT = 3  # seconds
HANDSHAKE_POLL_SLEEP = 0.05  # seconds
HANDSHAKE_POLL_ATTEMPTS = int((HANDSHAKE_TIMEOUT * 1000) / HANDSHAKE_POLL_SLEEP)


logger = logging.getLogger(__name__)


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu*')
        # ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    logger.info(f"Found available ports: {ports}")
    return ports


class MotorController(object):
    def __init__(self):
        self._serial = None
        self._initialized = False

    @classmethod
    def instance(cls):
        return _instance

    def initialize(self):
        self._serial = self.get_serial()
        if self._serial is None:
            return False, 'failed to open serial connection'
        self._initialized = True
        return True, ''

    def get_controller_serial_status(self):
        port = Configuration.config().get('arduino_port')
        baudrate = Configuration.config().get('serial_baudrate')
        timeout = Configuration.config().get('serial_timeout')

        logger.info(f"starting initialization port={port} baud={baudrate} timeout={timeout}")

        checks = {
            'initialized': self._initialized,
            'serial': {
                'status': 'NOT OK',
                'message': '',
            }
        }
        if not self._initialized:
            checks['serial']['message'] = "serial port not initialized"
            logger.info("serial port not initialized")
            return checks

        for i in range(CONNECT_POLL_ATTEMPTS):
            if self._serial.is_open:
                logger.info("serial port opened successfully")
                break
            time.sleep(CONNECT_POLL_SLEEP)

        if not self._serial.is_open:
            checks['serial']['status'] = 'NOT OK'
            checks['serial']['message'] = 'could not open connection to serial port'
            logger.info("failed to open connection to port")
        else:
            if not self._confirm_with_handshake(self._serial):
                checks['serial']['status'] = 'NOT OK'
                checks['serial']['message'] = 'no ACK received'
                logger.info("failed to receive ACK")
            else:
                checks['serial']['status'] = 'OK'
                logger.info("initialization complete")

        return checks

    def _find_port(self):
        logger.info("Finding a worthy port")
        available_ports = serial_ports()
        for port in available_ports:
            logger.info(f"[{port}]")
            confirmed_handshake = False
            s = serial.Serial(port=port, baudrate=self.baudrate, timeout=self.timeout)
            for i in range(CONNECT_POLL_ATTEMPTS):
                if s.is_open:
                    logger.info("   ...connected")
                    confirmed_handshake = self._confirm_with_handshake(s)
                    break
                time.sleep(CONNECT_POLL_SLEEP)
            s.close()
            if confirmed_handshake:
                logger.info("   ...ACKed!")
                return port
            logger.info("   ...no ACK")
        return None

    def _confirm_with_handshake(self, _serial):
        timeout = Configuration.config().get('serial_timeout')
        for i in range(5):
            _serial.write(bytes(f"{HANDSHAKE}:", 'utf-8'))
            time.sleep(1)
            data = _serial.readline()
            attempts = int(HANDSHAKE_TIMEOUT / (HANDSHAKE_POLL_SLEEP + timeout))
            for i in range(attempts):
                data = _serial.readline().decode('utf-8').strip()
                if data == HANDSHAKE_ACK:
                    return True
                if i < attempts - 1:
                    time.sleep(HANDSHAKE_POLL_SLEEP)
        return False

    def get_serial(self):
        if self._serial:
            return self._serial
        port = Configuration.config().get('arduino_port')
        baudrate = Configuration.config().get('serial_baudrate')
        timeout = Configuration.config().get('serial_timeout')
        _serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        for i in range(CONNECT_POLL_ATTEMPTS):
            if _serial.is_open:
                logger.info("serial port opened successfully")
                self._confirm_with_handshake(_serial)
                self._serial = _serial
                return self._serial
            time.sleep(CONNECT_POLL_SLEEP)
        return None

    # TODO: not sure how port detection will play with the rest of the flow yet
    # def configure(self, port=None, baudrate=None, timeout=None):
    #     # TODO: should we just set port, baudrate, and timeout in config
    #     # and read directly from there?
    #     logger.info("# Starting MotorController configure #")
    #     if baudrate is not None:
    #         self.baudrate = baudrate
    #     if timeout is not None:
    #         self.timeout = timeout

    #     if port is not None:
    #         self.port = port
    #         return
    #     else:
    #         self.port = self._find_port()
    #         if not self.port:
    #             msg = "Failed to find a port that is worthy"
    #             logger.error(msg)
    #             raise Exception(msg)

    #     logger.info(f"--> MotorController: port={self.port}, baudrate={self.baudrate}, timeout={self.timeout}")
    #     self._serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
    #     # Serial may not open right away.. give it a little bit
    #     for i in range(CONNECT_POLL_ATTEMPTS):
    #         if self._serial.is_open:
    #             logger.info(f"    Connected to {self.port}!")
    #             return
    #         time.sleep(CONNECT_POLL_SLEEP)

    #     msg = f"Failed to connect to {self.port}"
    #     logger.error(msg)
    #     raise Exception(msg)

    def write_read(self, cmd):
        if not self._initialized:
            raise MotorControllerException('controller not initialized')
        _serial = self.get_serial()
        _serial.write(bytes(cmd, 'utf-8'))
        time.sleep(0.05)
        response = []
        data = _serial.readline()
        while data:
            data = _serial.readline().decode('utf-8').strip()
            response.append(data)
        return response

    def hand_open(self):
        logger.info('Performing hand:open')
        return self.write_read('hand:open')

    def hand_close(self):
        logger.info('Performing hand:close')
        return self.write_read('hand:close')

    def z_down(self):
        logger.info('Performing z:down')
        return self.write_read('z:down')

    def z_up(self):
        logger.info('Performing z:up')
        return self.write_read('z:up')


_instance = MotorController()
