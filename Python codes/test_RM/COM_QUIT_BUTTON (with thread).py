#!/usr/bin/env python

## 1. Importing maltplotlib - allows display of graphics in the way matlab does
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

## Importing numpy - numerical library 
from numpy import *
##import numpy

from matplotlib.figure import Figure

import sys
from Tkinter import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
import tkMessageBox

import numpy as np
from collections import deque
import time
from time import sleep
import csv
import serial




## Step 1: An object of class Tk is instantiated. For more info, read https://docs.python.org/2/library/tkinter.html
root = Tk.Tk()
root.wm_title("Embedding in TK")
##analogPlot = COMPortDAQ('COM3',115200)

## Step 2 : Figure is being made (not yet included in the GUI object). For more info read: http://matplotlib.org/api/figure_api.html
f = Figure(figsize=(5, 4), dpi=100)

def makeSubplot(theFigure, position, title, xlabel, ylabel):
    theSubplot = theFigure.add_subplot(position)
    theSubplot.set_title(title)
    theSubplot.set_xlabel(xlabel)
    theSubplot.set_ylabel(ylabel)
    return theSubplot
ax = makeSubplot(f, 321, 'A(x)','time','m/s')
ay = makeSubplot(f, 323, 'A(y)','time','m/s')
az = makeSubplot(f, 325, 'A(z)','time','m/s')
gx = makeSubplot(f, 322, 'G(x)','time','deg/s')
gy = makeSubplot(f, 324, 'G(y)','time','deg/s')
gz = makeSubplot(f, 326, 'G(z)','time','deg/s')
t = arange(0.0, 3.0, 0.01)

#ax.plot(t, sin(2*pi*t))
#ay.plot(t, cos(2*pi*t))

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


def on_key_event(event):
    print('you pressed %s' % event.key)
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect('key_press_event', on_key_event)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent

quitButton = Tk.Button(master=root, text='QUIT', command=_quit)
quitButton.pack(side=Tk.RIGHT)

def StartStopButton():
	if startstop["text"] == 'START':
		startstop["text"]='STOP'
##		print(analogPlot.selectedCOMPort)
##		analogPlot.openPort()
##		analogPlot.setFileInfo('test_python.csv')
##		analogPlot.writeToCSVFile()
	else:
		startstop["text"]='START'
##		analogPlot.close()
			
		
startstop = Tk.Button(master=root, text='START',command=StartStopButton)
startstop.pack(side=Tk.LEFT)

def OKButtoncallBack(okButtonHandle,comListHandle,selectedCOMPort): 
    value = comListHandle.get(comListHandle.curselection())
    analogPlot.selectedCOMPort = str(value)
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
 
comportButton = Tk.Button(master=root, text='COM Port', command=comportButtonCallBack)
comportButton.pack(side=Tk.LEFT)
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


Tk.mainloop()
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.
