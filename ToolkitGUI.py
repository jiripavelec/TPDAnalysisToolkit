import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import ControlsFrame#, Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from PlotsFrame import PlotsFrame, MPLContainer
from os import listdir
from os.path import isfile, join
import multiprocessing
import sys

class MainFrame(tk.Frame):
    def __init__(self, root):#, parent, controller):
        super().__init__()
        self.initUI(root)

    def initUI(self, root):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        self.m_panedWindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.m_panedWindow.pack(side=tk.LEFT, fill = tk.BOTH, expand=True)
        self.plotsFrame = PlotsFrame(self.m_panedWindow, bg ='white') #need to init this first, because the controls will request notebooks/plots inside plotsframe
        self.controlsFrame = ControlsFrame(self.m_panedWindow, root, self.plotsFrame, bg = 'white', relief='groove')
        
        self.m_panedWindow.add(self.controlsFrame)
        self.m_panedWindow.add(self.plotsFrame)

        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()

    def resetResizeTime(self, event):
        if(not isinstance(event.widget, tk.Tk)): # only care about main window (root) resizing
            return
        elif( (not (self.lastWidth == event.width)) or (not (self.lastHeight == event.height))):
            self.controlsFrame.resetResizeTime()
            self.lastWidth = event.width
            self.lastHeight = event.height
        #else we didnt resize as the dimensions have not changed

def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame(root)
    # if not sys.platform.startswith('win'):
    root.bind('<Configure>',main.resetResizeTime)
    root.mainloop()

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    main()

