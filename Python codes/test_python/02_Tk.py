#!/usr/bin/env python

import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure

import sys
from Tkinter import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
import tkMessageBox


root = Tk.Tk()
root.wm_title("Yeh terrace ke naam")


f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)
t = arange(0.0, 3.0, 0.01)
s = sin(2*pi*t)

a.plot(t, s)


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

def OKButtoncallBack(okButtonHandle,comListHandle,selectedCOMPort): 
    value = comListHandle.get(comListHandle.curselection())
    selectedCOMPort = str(value)
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
