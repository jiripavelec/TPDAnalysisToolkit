import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import ControlsFrame#, Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from PlotsFrame import PlotsFrame, MPLContainer
from os import listdir
from os.path import isfile, join
import multiprocessing
import sys
import cProfile, pstats, io
from pstats import SortKey

class ExtendedRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.m_onResizeCallbacks = list()
        self.m_lastResizeTime = datetime.now()
        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()
        self.m_resizeHandledOnce = False
        self.m_resizeHandledTwice = False

    def registerResizeCallback(self, callback):
        self.m_onResizeCallbacks.append(callback)

    def allCallbacks(self,timeDelta):
        for c in self.m_onResizeCallbacks:
            c(timeDelta) #pass the timedelta to each callback

    def resizeAnimation(self):
        now = datetime.now()
        timeDelta = now - self.m_lastResizeTime #get timedelta since last resize event
        if(not self.m_resizeHandledOnce):
            self.allCallbacks(timeDelta)
            self.m_resizeHandledOnce = True
        elif(timeDelta.total_seconds()*1000 > 700 and not self.m_resizeHandledTwice): #every 300ms call the callbacks
            self.allCallbacks(timeDelta)
            self.m_resizeHandledTwice = True
        self.after(300,self.resizeAnimation)

    def resetResizeTime(self, event):
        if(not isinstance(event.widget, tk.Tk)): # only care about main window (root) resizing
            return
        elif( (not (self.lastWidth == event.width)) or (not (self.lastHeight == event.height))):
            self.m_lastResizeTime = datetime.now()
            self.m_resizeHandledOnce = False
            self.m_resizeHandledTwice = False
            # self.controlsFrame.resetResizeTime()
            self.lastWidth = event.width
            self.lastHeight = event.height

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

        # self.m_panedWindow.paneconfigure(self.controlsFrame, minsize = self.controlsFrame.getMinWidth())

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
    root = ExtendedRoot()
    root.geometry("1920x1080")
    main = MainFrame(root)
    # if not sys.platform.startswith('win'):
    # root.bind('<Configure>',main.resetResizeTime)
    root.bind('<Configure>',root.resetResizeTime)
    # pr = cProfile.Profile()
    # pr.enable()
    root.after(300,root.resizeAnimation)
    root.mainloop()
    # pr.disable()
    # pr.dump_stats("output.prof")
    # s = io.StringIO()
    # sortby = SortKey.CUMULATIVE
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    main()

