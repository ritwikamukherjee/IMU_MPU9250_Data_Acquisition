import sys, serial, argparse
import numpy as np
import time
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
		self.az = deque([0.0]*maxLen)
		self.at = deque([0.0]*maxLen)
		self.au = deque([0.0]*maxLen)
		self.av = deque([0.0]*maxLen)
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
	  assert(len(data) == 6)
	  self.addToBuf(self.ax, data[0])
	  self.addToBuf(self.ay, data[1])
	  self.addToBuf(self.az, data[2])
	  self.addToBuf(self.at, data[3])
	  self.addToBuf(self.au, data[4])
	  self.addToBuf(self.av, data[5])

  def setFileInfo(self,filename):
	#adding to csv 
	self.acsvFile = open(filename, 'wb') 
	self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
	print("File info has been set...")
	self.acsvwriter.writerow(['TempA', 'TempB', 'TempC', 'TempD', 'TempE', 'TempF', 'Time'])
	
  #adding into the csv	  
  def writeToCSVFile(self, data):
	print('Writing', data[0], data[1], data[2], data[3], data[4], data[5], time.clock())
	self.acsvwriter.writerow([data[0], data[1], data[2], data[3], data[4], data[5], time.clock()])
 
 
  # update plot
  def update(self, frameNum, a0, a1, a2, a3, a4, a5):
      try:
		  line = self.ser.readline()
		  data = [float(val) for val in line.split()]
		  self.writeToCSVFile(data)
		  # print data
		  if(len(data) == 6):
				self.add(data)
				a0.set_data(range(self.maxLen), self.ax)
				a1.set_data(range(self.maxLen), self.ay)
				a2.set_data(range(self.maxLen), self.az)
				a3.set_data(range(self.maxLen), self.at)
				a4.set_data(range(self.maxLen), self.au)
				a5.set_data(range(self.maxLen), self.av)
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
	#f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
	fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, sharex='col', sharey='row')
	
	# intialize two line objects (one in each axes)
	  
	
	a0, = ax1.plot([], [])           # line objects
	a1, = ax2.plot([], [], color='r')
	a2, = ax3.plot([], [], color='g')
	a3, = ax4.plot([], [], color='m')
	a4, = ax5.plot([], [], color='k')
	a5, = ax6.plot([], [], color='c')
	#line=[a0,a1,a2,a3,a4,a5]
	for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
		ax.set_ylim(0,1023)
		ax.set_xlim(0, 100)
		ax.grid()
		ax.figure.canvas.draw()
	
	# update the data of both line objects
    #line[0].set_data(xdata, a0)
    #line[1].set_data(xdata, a1)

    #return line

	
	anim1 = animation.FuncAnimation(fig, analogPlot.update, 
						 fargs=(a0,a1,a2,a3,a4,a5), 
						 interval=50)



	

	# show plot
	plt.show()

	# clean up
	analogPlot.close()
  

# call main
if __name__ == '__main__':
  main()