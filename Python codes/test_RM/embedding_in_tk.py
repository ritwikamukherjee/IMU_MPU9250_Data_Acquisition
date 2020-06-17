#!/usr/bin/env python

import matplotlib

matplotlib.use('TkAgg')

import numpy as np
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

import matplotlib.pyplot as plt

from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

root = Tk.Tk()
root.wm_title("Embedding in TK")
##
def f(t):
    return np.exp(-t) * np.cos(2*np.pi*t)

t1 = np.arange(0.0, 5.0, 0.1)
t2 = np.arange(0.0, 5.0, 0.02)
plt.Figure()
f = plt.get_current_fig_manager()
plt.subplot(211)
plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')

plt.subplot(212)
plt.plot(t2, np.cos(2*np.pi*t2), 'r--')
plt.show()
##f = Figure(figsize=(5, 4), dpi=100)
##ax = f.add_subplot(321)
##gx = f.add_subplot(322)
##ay = f.add_subplot(323)
##gy = f.add_subplot(324)
##az = f.add_subplot(325)
##gz = f.add_subplot(326)
##t = arange(0.0, 3.0, 0.01)
##s = sin(2*pi*t)
##
##ax.plot(t, s)
##f.suptitle("Real Time plots", fontsize="x-large")
##ax.set_title("Accel(x)")
##ay.set_title("Accel(y)")
##az.set_title("Accel(z)")
##gx.set_title("Gyro(x)")
##gy.set_title("Gyro(y)")
##gz.set_title("Gyro(z)")

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
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = Tk.Button(master=root, text='Quit', command=_quit)
button.pack(side=Tk.BOTTOM)

Tk.mainloop()
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.
