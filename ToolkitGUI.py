import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import ControlsFrame#, Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from PlotsFrame import PlotsFrame, MPLContainer
from os import listdir
from os.path import isfile, join

class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)
        #TODO: consider using tkinter PanedWindow for draggable divider
        #see
        #https://stackoverflow.com/questions/27102077/make-stretchable-split-screen-in-tkinter
        #and
        #http://effbot.org/tkinterbook/panedwindow.htm

        self.plotsFrame = PlotsFrame(self, bg ='white')
        self.plotsFrame.place(relx = 0.25, rely = 0.0, relwidth = 0.75, relheight = 1.0, anchor = "nw", bordermode = tk.INSIDE)

        self.controlsFrame = ControlsFrame(self, bg = 'white', relief='groove')
        self.controlsFrame.place(relx = 0.0, rely = 0.0, relwidth = 0.25, relheight = 1.0, anchor = "nw", bordermode = tk.INSIDE)
        self.controlsFrame.initChords(self.plotsFrame)

        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()

    def resetResizeTime(self, event):
        if( (not (self.lastWidth == self.winfo_width)) or (not (self.lastHeight == self.winfo_height))):
            self.controlsFrame.resetResizeTime()
            # self.leftFrame.Controls.m_notebook.resizeDateTime = datetime.now()
            self.lastWidth = self.winfo_width
            self.lastHeight = self.winfo_height
        #else we didnt resize as the dimensions have not changed

def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame()
    root.bind('<Configure>',main.resetResizeTime)
    root.mainloop()

if __name__ == '__main__':
    main()

