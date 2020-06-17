import serial

ser = serial.Serial('COM3', 9600, timeout=1)
line = ser.readline()   # read a '\n' terminated line
ser.close()