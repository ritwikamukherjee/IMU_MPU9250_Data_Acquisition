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

from matplotlib import animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib
from matplotlib import pyplot as plt
import threading
######


aFlag = -1

## Serial Data Acquisition Class - the class reads from serial port and write to a csv file
##
class SerialDAQ:
##                
	def __init__(self, strPort):
                self.serialPort = strPort
##                initbuffer()
                
	def __init__(self, strPort, bdRate):
                self.serialPort = strPort
                self.baudRate   = bdRate
##                initbuffer()
	def __init__(self, strPort, bdRate, fname):
                self.serialPort = strPort
                self.baudRate   = bdRate
                self.filename = fname
                self.vv=1
                self.axbuffer = [0]*100;
                self.aybuffer = range(0,100);
                self.azbuffer = [0]*100;
                self.gxbuffer = [0]*100;
                self.gybuffer = [0]*100;
                self.gzbuffer = [0]*100;

        def updateBuffer(uData):
                self.axbuffer.pop(0)
                self.axbuffer.append(uData[0])
                print('here')

	def close(self):
		self.ser.flush()
		self.ser.close()    
		self.acsvFile.close()
		print("Goodbye")

	def start(self):
		self.ser = serial.Serial(self.serialPort, self.baudRate)
		self.acsvFile = open(self.filename, 'wb') 
		self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
		self.acsvwriter.writerow(['AccX', 'AccY', 'AccZ', 'GyrX', 'GyrY', 'GyrZ', 'Temp', 'Arduino Time period counter', 'Computer time of Data writing'])

	def setSetialPort(self, strPort):
		self.serialPort = strPort

	def setFileInfo(self,fname):
                self.filename = fname
		
	def writeToCSVFile(self):
##                try:
##                        first = unpack('!b',self.ser.read(1))  #read the first two bytes and setting it according to arduino register code
##                        if (first[0]==3):
##                            second = unpack('!b',self.ser.read(1))
##                            if (second[0]==31):
##                                data = unpack('!hhhhhhhH',self.ser.read(16)) #call the next 14 from registers?
##                                self.acsvwriter.writerow([data[0], data[1], data[2], data[4], data[5], data[6], data[3], data[7], time.clock()])
##                                self.updateBuffer(data[0])
                try:
                        first = unpack('!h',self.ser.read(2))  #read the first two bytes and setting it according to arduino register code
                        if (first[0]==799):
                                data = unpack('!hhhhhhhH',self.ser.read(16)) #call the next 14 from registers?
                                self.acsvwriter.writerow([data[0], data[1], data[2], data[4], data[5], data[6], data[3], data[7], time.clock()]) #

                except:
                        print('Not the starting of the data stream')

        def run(self,bb,aflag):
                print 'Running'
                self.ser.flush()
                while (not aflag.is_set()):
                    self.writeToCSVFile()
                print 'out'

##########################################################################################################
##class App(threading.Thread):
##    def __init__(self):
##        threading.Thread.__init__(self)
##
##    def     
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

def testfunc(aa,aFlag):
    print 'in testfunc'
    print aFlag.is_set()
    print 


def main():
##        Create root/main window
## Step 1: An object of class Tk is instantiated. For more info, read https://docs.python.org/2/library/tkinter.html
        rootWindow = Tk.Tk()
        rootWindow.wm_title("Real-Time DAQ")
## Step 2 : Figure is being made (not yet included in the GUI object). For more info read: http://matplotlib.org/api/figure_api.html
        f = Figure(figsize=(5, 4), dpi=100)
        fig = plt.figure()
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
        theDAQ = SerialDAQ("COM3",115200,'test_python.csv')
        global threadNum
        threadNum = 1
        tTFlag = threading.Event()
        tthread = threading.Thread(target=theDAQ.run,args=(1,tTFlag), name = "TheThread-{}".format(threadNum))
        startFlag = threading.Event()
##        def refresh():
##            while (not startFlag.is_set()):
##                print 'aaaa'
##                time.sleep(1)
##        refreshThread = threading.Thread(target=refresh, name = "Refresh-{}".format(threadNum))
##        refreshThread.start()
        def StartStopButton(tthread):
                global threadNum
                if startstop["text"] == 'START':
                        startstop["text"]='STOP'
                        theDAQ.start()
                        print 'Started'
                        print threadNum
                        tTFlag.clear()
                        if(threadNum!=1):
                            tthread = threading.Thread(target=theDAQ.run,args=(1,tTFlag), name = "TheThread-{}".format(threadNum))
                        print tthread.getName()
                        tthread.start()
                else:
                        startstop["text"]='START'
                        tTFlag.set()
                        theDAQ.close()
                        tthread.join()
                        threadNum=threadNum+1


        startstop = Tk.Button(master=rootWindow, text='START',command=lambda: StartStopButton(tthread))
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
  
