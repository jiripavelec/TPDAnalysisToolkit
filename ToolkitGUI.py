import tkinter as tk
import tkinter.ttk as ttk

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        leftFrame = tk.Frame(self)
        


        rightFrame = tk.Frame(self)

