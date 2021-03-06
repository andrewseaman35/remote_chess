import serial
import time

PORT_NAME = '/dev/cu.usbmodem143101'
BAUD_RATE = 9600


def write_read(x):
    arduino = serial.Serial(port=PORT_NAME, baudrate=BAUD_RATE, timeout=1)
    while not arduino.is_open:
        print('not open')
        time.sleep(0.5)
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    response = []
    data = arduino.readline()
    while data:
        response.append(data.decode('utf-8').strip())
        data = arduino.readline();

    return '\n'.join(response)

while True:
    num = input("Enter a string: ")
    value = write_read(num)
    print(value)
    print('-- end --')
