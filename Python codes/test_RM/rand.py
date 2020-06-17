
import Tkinter as tk
class MyWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Hello, world")
        label.pack()
        label.bind("<1>", self.quit)
    def quit(self):
        sys.exit()

root = tk.Tk()
MyWindow(root).pack()
root.mainloop()
