import serial
import time
import numpy as np
from matplotlib import pyplot as plt


ser = serial.Serial('COM3',9600)

plt.ion() # set plot to animated
ydata = [0] * 10
ax1=plt.axes() 

# make plot
#plt.ylim([100,400])
line, = plt.plot(ydata)

#for ii in range(1,10):
while True:
	aa = ser.readline()
	bb = aa.split()
	ydata.append(bb[0])
	line.set_xdata(np.arange(len(ydata)))
	line.set_ydata(ydata)  # update the data
#	time.sleep(1)
	plt.show()
	#print '%d %d' % (int(bb[0]), int(bb[1]))
	
	
#	plt.plot(bb)
	
	
#while True:  
#	data = ser.readline() # read data from serial 
#	bb = data.split()
#	if len(bb) == 2:
#		ydata.append(bb[1])
#        del ydata[0]
#        line.set_xdata(np.arange(len(ydata)))
#        line.set_ydata(ydata)  # update the data
#        plt.draw() # update the plot
#	time.sleep(1)
ser.close()




