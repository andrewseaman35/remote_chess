import serial
import time

PORT_NAME = '/dev/cu.usbmodem143101'
BAUD_RATE = 9600


arduino = serial.Serial(port=PORT_NAME, baudrate=BAUD_RATE, timeout=1)
def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    while data:
        print(data)
        data = arduino.readline();

    return data

while True:
    num = input("Enter a string: ")
    value = write_read(num)
    print('-- end --')
