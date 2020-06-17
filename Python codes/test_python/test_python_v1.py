import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque

import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import csv

    
# plot class
class AnalogPlot:
  # constr
  def __init__(self, strPort, maxLen):
      # open serial port
      self.ser = serial.Serial("COM3", 9600)

      self.ax = deque([0.0]*maxLen)
      self.ay = deque([0.0]*maxLen)
      self.maxLen = maxLen

  # add to buffer
  def addToBuf(self, buf, val):
      if len(buf) < self.maxLen:
          buf.append(val)
      else:
          buf.pop()
          buf.appendleft(val)

  # add data
  def add(self, data):
      assert(len(data) == 2)
      self.addToBuf(self.ax, data[0])
      self.addToBuf(self.ay, data[1])

  def setFileInfo(self,filename):
	#adding to csv 
	self.acsvFile = open(filename, 'wb') 
	self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
	print("File info has been set...")
	self.acsvwriter.writerow(['TempA', 'TempB'])
	
  #adding into the csv	  
  def writeToCSVFile(self, data):
	print('Writing', data[0], data[1])
	self.acsvwriter.writerow([data[0],data[1]])
 
 
  # update plot
  def update(self, frameNum, a0, a1):
      try:
		  line = self.ser.readline()
		  data = [float(val) for val in line.split()]
		  self.writeToCSVFile(data)
		  # print data
		  if(len(data) == 2):
			  self.add(data)
			  a0.set_data(range(self.maxLen), self.ax)
			  a1.set_data(range(self.maxLen), self.ay)
      except KeyboardInterrupt:
          print('exiting')
      
      return a0, 
	  

 # clean up
  def close(self):
      # close serial
		self.ser.flush()
		self.ser.close()    
		self.acsvFile.close()
		print("Closed all")
	
#main() function
def main():	
	# create parser
	parser = argparse.ArgumentParser(description="LDR serial")
	# add expected arguments
	parser.add_argument('--port', dest='ritwikasport', required=True)

	# parse args
	args = parser.parse_args()

	#strPort = 'COM3'
	strPort = args.ritwikasport

	print('reading from serial port %s...' % strPort)

	# plot parameters
	analogPlot = AnalogPlot(strPort, 100)
	analogPlot.setFileInfo('test_python.csv')
	print('plotting data...')
	# set up animation

	fig = plt.figure()
	ax = plt.axes(xlim=(0, 100), ylim=(0, 1023))
	a0, = ax.plot([], [])
	a1, = ax.plot([], [])
	anim = animation.FuncAnimation(fig, analogPlot.update, 
								 fargs=(a0,a1), 
								 interval=50)
	

	# show plot
	plt.show()

	# clean up
	analogPlot.close()
  

# call main
if __name__ == '__main__':
  main()