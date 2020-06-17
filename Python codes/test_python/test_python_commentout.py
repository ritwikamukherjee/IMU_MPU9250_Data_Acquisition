import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque
import time
import csv
from struct import *   
# plot class
class AnalogPlot:
  # constr
	def __init__(self, strPort, maxLen):
		self.ser = serial.Serial(strPort, 115200)

	def close(self):
		self.ser.flush()
		self.ser.close()    
		self.acsvFile.close()
		print("Closed all")


	def setFileInfo(self,filename):
	#adding to csv 
		self.acsvFile = open(filename, 'wb') 
		self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
		print("File info has been set...")
		self.acsvwriter.writerow(['AccX', 'AccY', 'AccZ', 'GyrX', 'GyrY', 'GyrZ', 'Time'])
		
	def writeToCSVFile(self):
		try:
                        aline = self.ser.read(16);
                        data = unpack('!hhhhhhhh',aline)
##                        print(data)
##                        data = [float(val) for val in unpackedline.split()]
                        if(len(data) == 8):
                                self.acsvwriter.writerow([data[1], data[2], data[3], data[5], data[6], data[7], time.clock()])
		except:
			print('Something is going wrong')
 # clean up
	def close(self):
      # close serial
		self.ser.flush()
		self.ser.close()    
		self.acsvFile.close()
		print("Closed all")
		
def main():
	print('reading from serial port %s...' )	
	analogPlot = AnalogPlot("COM3", 100)
	analogPlot.setFileInfo('test_python.csv')
	while time.clock()<10:
                try:
                        line = analogPlot.writeToCSVFile()
                except:
                        print('Wrong')
####		analogPlot.writeToCSVFile()
##	print('plotting data...')		
	analogPlot.close()
	

	

# call main
if __name__ == '__main__':
	main()
  
