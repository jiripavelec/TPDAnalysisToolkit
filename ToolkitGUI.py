import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from Controls import ControlsFrame, Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from ProcessRawDataControl import ProcessRawDataControl
from InvertDataControl import InvertDataControl
from PlotsFrame import PlotsFrame, MPLContainer
from os import listdir
from os.path import isfile, join

# from dt import timedelta






class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.ControlArray = []
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        self.ControlArray.append(ProcessRawDataControl(bg = "white"))
        self.ControlArray.append(InvertDataControl())

        self.plotsFrame = PlotsFrame(self, bg ='white')
        # self.plotsFrame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        self.plotsFrame.grid(row = 0, column = 1, sticky = "nsew")

        self.controlsFrame = ControlsFrame(self, bg = 'white', relief='groove')
        # self.controlsFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        self.controlsFrame.grid(row = 0 , column = 0, sticky = "nsew")

        self.grid_columnconfigure(index = 0, weight = 1)
        self.grid_columnconfigure(index = 1, weight = 5)
        self.grid_rowconfigure(index = 0, weight = 1)

        for c in self.ControlArray:
            c.initNotebook(self.plotsFrame)
            c.initChordUI(self.controlsFrame.accordion)

        self.controlsFrame.initChords([c.m_chord for c in self.ControlArray])

        # self.resizeTimer = datetime.now()
        # self.rightFrame.resizeTest()
        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()
    # def resizePlots(self):
    #     self.rightFrame.resizeTest()

    def resetResizeTime(self, event):
        if( (not (self.lastWidth == self.winfo_width)) or (not (self.lastHeight == self.winfo_height))):
            for c in self.ControlArray:
                c.setResizeTime()
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

