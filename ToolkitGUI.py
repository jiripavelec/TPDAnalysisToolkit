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

#The tkinter root window is managed by an instance of the tk.Tk class.
#Here we simply derive from the class to give it some extended functionality in an object-oriented programming style.
class ExtendedRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.m_onResizeCallbacks = list() #this is a list of callbacks (so functions to be called on a certain event, in this case, onResize)
        self.m_lastResizeTime = datetime.now() #we keep track of resizing events, because the matplotlib is not meant for realtime rendering, and we need this for some workarounds
        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()
        self.m_resizeHandledOnce = False
        self.m_resizeHandledTwice = False

    def registerResizeCallback(self, callback):
        self.m_onResizeCallbacks.append(callback)

    def allCallbacks(self,timeDelta): #call all onResize callbacks
        for c in self.m_onResizeCallbacks:
            c(timeDelta) #pass the timedelta to each callback

    def resizeAnimation(self):  #the resizeAnimation function effectively throttles the resize events we actually deal with
                                #if we wouldn't throttle the response, the UI would be unusable during resize
        now = datetime.now()
        timeDelta = now - self.m_lastResizeTime #get timedelta since last resize event
        if(not self.m_resizeHandledOnce): #first response is immedate, to keep the UI feeling responsive
            self.allCallbacks(timeDelta)
            self.m_resizeHandledOnce = True
        # responses after the first are dealt with on a periodic basis
        elif(timeDelta.total_seconds()*1000 > 700 and not self.m_resizeHandledTwice): #every 300ms call the callbacks
            self.allCallbacks(timeDelta)
            self.m_resizeHandledTwice = True
        self.after(350,self.resizeAnimation)

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

#The MainFrame is the first child of the root Window, and as such our first custom UI frame
#It consists of a panedWindow with two frames.
# 1) The PlotsFrame, containing plots in a NoteBook/Tab fashion.
# 2) The ControlsFrame, containing an accordion of all controls. See ControlElements for the accordion class.
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

#Every program needs a main function. Here we have the main function starting our UI
def main():
    root = ExtendedRoot() #instantiate tk.Tk root window
    root.geometry("1920x1080") #set window size (arbitrary for now, you can resize the window manually anyway)
    main = MainFrame(root)
    root.bind('<Configure>',root.resetResizeTime)#we bind the resetResizeTime function to the <Configure> event.
    # COMMENTS BELOW HERE ARE THE REMAINDER OF SOME DEBUG PROFILING CODE. They have not been deleted to make enabling profiling easier.
    # One could also enable the code on basis of some boolean value.
    # pr = cProfile.Profile()
    # pr.enable()
    root.after(500,root.resizeAnimation)
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
        # On Windows calling this function is necessary. Multiprocessing freezes the UI otherwise, and noone likes frozen UI's
        multiprocessing.freeze_support()
    main()

