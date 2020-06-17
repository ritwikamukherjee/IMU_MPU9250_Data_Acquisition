import sys, serial, argparse
import numpy as np
import time
import csv
from struct import *   


## Serial Data Acquisition Class - the class reads from serial port and write to a csv file
##
class SerialDAQ:
##                
	def __init__(self, strPort):
                self.serialPort = strPort

	def __init__(self, strPort, bdRate):
                self.serialPort = strPort
                self.baudRate   = bdRate
	def __init__(self, strPort, bdRate, fname):
                self.serialPort = strPort
                self.baudRate   = bdRate
                self.filename = fname

	def close(self):
		self.ser.flush()
		self.ser.close()    
		self.acsvFile.close()
		print("Goodbye")

	def start(self):
		self.ser = serial.Serial(self.serialPort, self.baudRate)
		self.acsvFile = open(self.filename, 'wb') 
		self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
		self.acsvwriter.writerow(['AccX', 'AccY', 'AccZ', 'GyrX', 'GyrY', 'GyrZ', 'Temp', 'Time'])

	def setSetialPort(self, strPort):
		self.serialPort = strPort

	def setFileInfo(self,fname):
                self.filename = fname
		
	def writeToCSVFile(self):
                try:
                        first = unpack('!h',self.ser.read(2))
                        if (first[0]==799):
                                data = unpack('!hhhhhhh',self.ser.read(14))
                                self.acsvwriter.writerow([data[0], data[1], data[2], data[4], data[5], data[6], data[3], time.clock()])
                except:
                        print('Not the starting of the data stream')


		
def main():
	theDAQ = SerialDAQ("COM3",115200,'test_python.csv')
	theDAQ.start()
	while time.clock()<10:
                try:
                        theDAQ.writeToCSVFile()
                except:
                        print('Error in writing to the File')
	theDAQ.close()

# call main
if __name__ == '__main__':
	main()
  
