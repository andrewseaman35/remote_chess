import serial
import time

PORT_NAME = '/dev/cu.usbmodem143101'
BAUD_RATE = 9600


arduino = serial.Serial(port=PORT_NAME, baudrate=BAUD_RATE, timeout=1)
def write_read(x):
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
    print('-- end --')
