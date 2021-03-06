import sys, serial, argparse
import numpy as np
import time
from time import sleep
from collections import deque
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib.figure import Figure
import csv

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import sys
from Tkinter import *
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
import tkMessageBox
    
# plot class
class AnalogPlot:
  # constr
  def __init__(self, strPort, maxLen):
      # open serial port
		self.ser = serial.Serial(strPort, 9600)

		self.ax = deque([0.0]*maxLen)
		self.ay = deque([0.0]*maxLen)
		self.az = deque([0.0]*maxLen)
		self.at = deque([0.0]*maxLen)
		self.au = deque([0.0]*maxLen)
		self.av = deque([0.0]*maxLen)
		#self.aw = deque([0.0]*maxLen)
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
	  #self.addToBuf(self.aw, data[6])

  def setFileInfo(self,filename):
	#adding to csv 
	self.acsvFile = open(filename, 'wb') 
	self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
	print("File info has been set...")
	self.acsvwriter.writerow(['AccX', 'AccY', 'AccZ', 'GyrX', 'GyrY', 'GyrZ', 'Time'])
	
  #adding into the csv	  
  def writeToCSVFile(self, data):
	#print('Writing', data[0], data[1], data[2], data[3], data[4], data[5], data[6], time.clock())
	if(len(data) == 6):
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
				#a6.set_data(range(self.maxLen), self.aw)
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
	root = Tk.Tk() ## Step 1: An object of class Tk is instantiated. For more info, read https://docs.python.org/2/library/tkinter.html
	root.wm_title("Embedding in TK")

	# plot parameters
	analogPlot = AnalogPlot("COM3", 100)
	analogPlot.setFileInfo('test_python.csv')
	print('plotting data...')
	
	# set up animation
	### Step 2 : Figure is being made (not yet included in the GUI object). For more info read: http://matplotlib.org/api/figure_api.html
	f = Figure(figsize=(5, 4), dpi=100)

	def makeSubplot(theFigure, position, title, xlabel, ylabel, ylim, xlim):
		theSubplot = theFigure.add_subplot(position)
		theSubplot.set_title(title)
		theSubplot.set_xlabel(xlabel)
		theSubplot.set_ylabel(ylabel)
		theSubplot.set_ylim(ylim)
		theSubplot.set_xlim(xlim)
		return theSubplot
	ax = makeSubplot(f, 321, 'A(x)','time','m/s',[-15000,15000],[0,100])
	ay = makeSubplot(f, 323, 'A(y)','time','m/s',[-15000,15000],[0,100])
	az = makeSubplot(f, 325, 'A(z)','time','m/s',[-15000,15000],[0,100])
	gx = makeSubplot(f, 322, 'G(x)','time','deg/s',[-15000,15000],[0,100])
	gy = makeSubplot(f, 324, 'G(y)','time','deg/s',[-15000,15000],[0,100])
	gz = makeSubplot(f, 326, 'G(z)','time','deg/s',[-15000,15000],[0,100])
	
	#fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, sharex='col', sharey='row')
	
	# intialize two line objects (one in each axes)
	 
	
	a0, = ax.plot([], [])           # line objects
	a1, = ay.plot([], [], color='r')
	a2, = az.plot([], [], color='g')
	a3, = gx.plot([], [], color='m')
	a4, = gy.plot([], [], color='k')
	a5, = gz.plot([], [], color='c')
	
	
		# a tk.DrawingArea
	
	def on_key_event(event):
		print('you pressed %s' % event.key)
		key_press_handler(event, canvas, toolbar)
	
	
	def _quit():
		analogPlot.close()
		root.quit()     # stops mainloop
		root.destroy()  # this is necessary on Windows to prevent# Fatal Python Error: PyEval_RestoreThread: NULL tstate
	
	
	canvas = FigureCanvasTkAgg(f, master=root)
	canvas.show()
	canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
	canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
	canvas.mpl_connect('key_press_event', on_key_event)
	button = Tk.Button(master=root, text='Quit', command=_quit)
	button.pack(side=Tk.BOTTOM)
	

    #return line

	def OKButtoncallBack(okButtonHandle,comListHandle,selectedCOMPort): 
		value = comListHandle.get(comListHandle.curselection())
		selectedCOMPort = str(value)
		okButtonHandle.quit()
		okButtonHandle.destroy()
		#Tk.mainloop()

	def comportButtonCallBack():
		aa = Toplevel()
		scrollbar = Scrollbar(aa)
		scrollbar.pack( side = RIGHT, fill=Y )
		mylist = Listbox(aa, yscrollcommand = scrollbar.set )
		for line in range(1,15):
			mylist.insert(END, "COM" + str(line))
		mylist.pack( side = LEFT, fill = BOTH )
		mylist.select_set(2)
		selectedCOMPort = "COM3"
		scrollbar.config(command = mylist.yview)
		OKButton = Tk.Button(master=aa, text="OK",command=lambda: OKButtoncallBack(aa,mylist,selectedCOMPort))
		OKButton.pack(side=RIGHT)
   
	comportButton = Tk.Button(master=root, text='COM Port', command=comportButtonCallBack)
	comportButton.pack(side=Tk.LEFT)
					# Fatal Python Error: PyEval_RestoreThread: NULL tstate


	anim1 = animation.FuncAnimation(f, analogPlot.update, 
						 fargs=(a0,a1,a2,a3,a4,a5), 
						 interval=50, blit=FALSE)

	
	Tk.mainloop()	
	
	print("animation done")
	#window = fig
	#window.withdraw()
 
	print("Animation set")
   # show plot
	plt.show()
	print("Plot shown")
	# clean up
	
	

# call main
if __name__ == '__main__':
  main()
  
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.	