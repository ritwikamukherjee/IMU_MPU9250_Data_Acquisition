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

aRes = 16.0/32768.0 ## case AFS_2G: aRes = 2.0/32768.0; case AFS_4G: aRes = 4.0/32768.0; case AFS_8G: aRes = 8.0/32768.0; case AFS_16G:aRes = 16.0/32768.0;
gRes = 1000.0/32768.0 ##GFS_250DPS: gRes = 250.0/32768.0;GFS_500DPS: gRes = 500.0/32768.0; GFS_1000DPS: gRes = 1000.0/32768.0; GFS_2000DPS: gRes = 2000.0/32768.0;
mRes = 10.*4912./32760.0 ##MFS_14BITS: mRes = 10.*4912./8190; MFS_16BITS: mRes = 10.*4912./32760.0; 
accelBias = [-0.19, -0.23, 0.01] ##making it [0,0,1]g
gyroBias = [-2.97, 0.63, 5.24]
MagCalibration = [1.2, 1.2, 1.16]
magBias = [-241.95, 279.61, -301.66]#z = -475.03
magScale = [1.17, 1.45, 0.69]

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
        self.tbuffer = range(0,1000);
        self.axbuffer = [0]*1000;
        self.aybuffer = [0]*1000;
        self.azbuffer = [0]*1000;
        self.gxbuffer = [0]*1000;
        self.gybuffer = [0]*1000;
        self.gzbuffer = [0]*1000;
        self.mxbuffer = [0]*1000;
        self.mybuffer = [0]*1000;
        self.mzbuffer = [0]*1000;
        self.flash = 0

    def close(self):
        self.ser.flush()
        self.ser.close()
        self.acsvFile.close()
        print("Goodbye")

    def start(self):
        self.ser = serial.Serial(self.serialPort, self.baudRate)
        self.acsvFile = open(self.filename, 'wb')
        self.acsvwriter = csv.writer(self.acsvFile, delimiter=',', dialect='excel')
        self.acsvwriter.writerow(['AccX', 'AccY', 'AccZ', 'GyrX', 'GyrY', 'GyrZ', 'MagX', 'MagY', 'MagZ', 'Temp', 'Arduino Time', 'LED FLASH', 'Computer time'])

	def setSerialPort(self, strPort):
		self.serialPort = strPort

	def setFileInfo(self,fname):
            self.filename = fname

    def writeToCSVFile(self):
			global aRes, gRes, accelBias, gyroBias, mRes, MagCalibration, magBias, magScale
			try:
				first = unpack('!h',self.ser.read(2))				#read the first two bytes and setting it according to arduino register code
				
				if (first[0]==799):
					data = unpack('!hhhhhhhhhhHb',self.ser.read(23)) #call the next 23 from registers?
					data = list(data)
					data[0] = data[0]*aRes #- accelBias[0] #subtraction here would give 0,0,1
					data[1] = data[1]*aRes #- accelBias[1]
					data[2] = data[2]*aRes #+ accelBias[2]
					data[4] = data[4]*gRes #- gyroBias[0]
					data[5] = data[5]*gRes #- gyroBias[1]
					data[6] = data[6]*gRes #- gyroBias[2]
					data[7] = data[7]*mRes #*MagCalibration[0] - magBias[0]
					#data[7] *= magScale[0]
					data[8] = data[8]*mRes #*MagCalibration[1] - magBias[1]
					#data[8] *= magScale[1]
					data[9] = data[9]*mRes #*MagCalibration[2] - magBias[2]
					#data[9] *= magScale[2]
					self.axbuffer.append(data[0])
					self.axbuffer.pop(0)
					self.aybuffer.append(data[1])
					self.aybuffer.pop(0)
					self.azbuffer.append(data[2])
					self.azbuffer.pop(0)
					self.gxbuffer.append(data[4])
					self.gxbuffer.pop(0)
					self.gybuffer.append(data[5])
					self.gybuffer.pop(0)
					self.gzbuffer.append(data[6])
					self.gzbuffer.pop(0)
					self.mxbuffer.append(data[7])
					self.mxbuffer.pop(0)
					self.mybuffer.append(data[8])
					self.mybuffer.pop(0)
					self.mzbuffer.append(data[9])
					self.mzbuffer.pop(0)
					flashnew = (data[11]-48)&1
					self.acsvwriter.writerow([data[0], data[1], data[2], data[4], data[5], data[6], data[7], data[8], data[9], data[3], data[10], flashnew, time.clock()])
					#if((flashnew==1) & (self.flash==0)):
					#    print 'Value changed to 1'
					#if((flashnew==0) & (self.flash==1)):
					 #   print 'Value changed to 0'
					self.flash = flashnew
			except:
				print('Not the starting of the data stream')

    def run(self,bb,aflag):
		print 'Running'
		self.ser.flush()
		while (not aflag.is_set()):
			self.writeToCSVFile()
		print 'out'

    def refreshplots(self,zz,bx,by,bz,cx,cy,cz,dx,dy,dz,aflag):
			while (not aflag.is_set()):
				bx.set_data(self.tbuffer,self.axbuffer)
				by.set_data(self.tbuffer,self.aybuffer)
				bz.set_data(self.tbuffer,self.azbuffer)
				cx.set_data(self.tbuffer,self.gxbuffer)
				cy.set_data(self.tbuffer,self.gybuffer)
				cz.set_data(self.tbuffer,self.gzbuffer)
				dx.set_data(self.tbuffer,self.mxbuffer)
				dy.set_data(self.tbuffer,self.mybuffer)
				dz.set_data(self.tbuffer,self.mzbuffer)
				return bx,

##########################################################################
##########################################################################
def makeSubplot(theFigure, position, title, xlabel, ylabel, ylim, xlim):
    theSubplot = theFigure.add_subplot(position)
    theSubplot.set_title(title)
    theSubplot.set_xlabel(xlabel)
    theSubplot.set_ylabel(ylabel)
    theSubplot.set_ylim(ylim)
    theSubplot.set_xlim(xlim)
    return theSubplot

def main():
##        Create root/main window
## Step 1: An object of class Tk is instantiated. For more info, read https://docs.python.org/2/library/tkinter.html
    rootWindow = Tk.Tk()
    rootWindow.wm_title("Real-Time DAQ")
## Step 2 : Figure is being made (not yet included in the GUI object). For more info read: http://matplotlib.org/api/figure_api.html
    f = Figure(figsize=(5, 4), dpi=100)
    ax = makeSubplot(f, 331, 'A(x)','time','g',[-10,10], [0,1000])
    ay = makeSubplot(f, 334, 'A(y)','time','g',[-10,10], [0,1000])
    az = makeSubplot(f, 337, 'A(z)','time','g',[-10,10], [0,1000])
    gx = makeSubplot(f, 332, 'G(x)','time','deg/s',[-700,700], [0,1000])
    gy = makeSubplot(f, 335, 'G(y)','time','deg/s',[-700,700], [0,1000])
    gz = makeSubplot(f, 338, 'G(z)','time','deg/s',[-700,700], [0,1000])
    mx = makeSubplot(f, 333, 'M(x)','time','0.1uT',[-700,700], [0,1000])
    my = makeSubplot(f, 336, 'M(y)','time','0.1uT',[-700,700], [0,1000])
    mz = makeSubplot(f, 339, 'M(z)','time','0.1uT',[-700,700], [0,1000])

    bx, = ax.plot([],[])
    by, = ay.plot([],[])
    bz, = az.plot([],[])
    cx, = gx.plot([],[])
    cy, = gy.plot([],[])
    cz, = gz.plot([],[])
    dx, = mx.plot([],[])
    dy, = my.plot([],[])
    dz, = mz.plot([],[])

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

    ##        https://docs.python.org/3/library/threading.html
    tTFlag = threading.Event() # Same link as above - 17.1.7
    tthread = threading.Thread(target=theDAQ.run,args=(1,tTFlag), name = "TheThread-{}".format(threadNum))
    startFlag = threading.Event()

##################
    anim1 = animation.FuncAnimation(f, theDAQ.refreshplots, fargs=(bx,by,bz,cx,cy,cz,dx,dy,dz,tTFlag), interval=50, blit=FALSE)
##################

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
##                            pthread = threading.Thread(target=theDAQ.refreshplot,args=(ax,tTFlag,bx), name="RefreshPlotT-{}".format(threadNum))
            print tthread.getName()
            tthread.start()
##                        pthread.start()
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
