import sys, serial, argparse
import numpy as np
import time
import csv
from struct import *   

######
from Tkinter import *
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib
import threading
######


aFlag = -1

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

##########################################################################################################
##########################################################################################################
		
def main2():        
	theDAQ = SerialDAQ("COM3",115200,'test_python.csv')
	theDAQ.start()
	while time.clock()<2:
                try:
                        theDAQ.writeToCSVFile()
                except:
                        print('Error in writing to the File')
	theDAQ.close()

####
def makeSubplot(theFigure, position, title, xlabel, ylabel):
    theSubplot = theFigure.add_subplot(position)
    theSubplot.set_title(title)
    theSubplot.set_xlabel(xlabel)
    theSubplot.set_ylabel(ylabel)
    return theSubplot

def main():
##        Create root/main window
## Step 1: An object of class Tk is instantiated. For more info, read https://docs.python.org/2/library/tkinter.html
        rootWindow = Tk.Tk()
        rootWindow.wm_title("Real-Time DAQ")
## Step 2 : Figure is being made (not yet included in the GUI object). For more info read: http://matplotlib.org/api/figure_api.html
        f = Figure(figsize=(5, 4), dpi=100)
        ax = makeSubplot(f, 321, 'A(x)','time','m/s')
        ay = makeSubplot(f, 323, 'A(y)','time','m/s')
        az = makeSubplot(f, 325, 'A(z)','time','m/s')
        gx = makeSubplot(f, 322, 'G(x)','time','deg/s')
        gy = makeSubplot(f, 324, 'G(y)','time','deg/s')
        gz = makeSubplot(f, 326, 'G(z)','time','deg/s')
        canvas = FigureCanvasTkAgg(f, master=rootWindow)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        def _quit():
            rootWindow.quit()     # stops mainloop
            rootWindow.destroy()  # this is necessary on Windows to prevent

        quitButton = Tk.Button(master=rootWindow, text='QUIT', command=_quit)
        quitButton.pack(side=Tk.RIGHT)
        def StartStopButton():
                if startstop["text"] == 'START':
                        startstop["text"]='STOP'
                        if aFlag==-1:
                                rootWindow.after(10,task)
                        aFlag =1                        
                else:
                        startstop["text"]='START'
                        aFlag =0

        startstop = Tk.Button(master=rootWindow, text='START',command=StartStopButton)
        startstop.pack(side=Tk.LEFT)
        def OKButtoncallBack(okButtonHandle,comListHandle,selectedCOMPort): 
            value = comListHandle.get(comListHandle.curselection())
            print str(value)
            okButtonHandle.quit()
            okButtonHandle.destroy()
            Tk.mainloop()

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

        comportButton = Tk.Button(master=rootWindow, text='COM Port', command=comportButtonCallBack)
        comportButton.pack(side=Tk.LEFT)
##
        
        Tk.mainloop()

# call main
if __name__ == '__main__':
	main()
  
