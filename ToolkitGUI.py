import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import * #ui element
from PlotsFrame import PlotsFrame
from tkinter.filedialog import askdirectory
from os import listdir
from os.path import isfile, join

# from dt import timedelta

class ProcessingStepControls:
    def __init__(self, title):
        self.m_title = title
        self.m_chordInitDone = False
        self.m_notebookInitDone = False
        self.mplContainers = []
        self.m_filesDirectory = ""

    def initChordUI(self, parent):
        raise NotImplementedError()

    def initNotebook(self, parent):
        raise NotImplementedError()

    def setResizeTime(self):
        for c in self.mplContainers:
            c.resizeDateTime = datetime.now()

    def selectFolder(self):
        raise NotImplementedError()


class ProcessTPDData(ProcessingStepControls):
    def __init__(self):
        super().__init__("Process TPD Data")

    def selectFolder(self):
        self.m_filesDirectory = askdirectory()
        [self.m_listBox.insert(0, f) for f in listdir(self.m_filesDirectory) if isfile(join(self.m_filesDirectory, f))]

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "Raw Data", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Processed Data", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)

        self.m_label = tk.Label(self.m_chord, text='Input files:')
        self.m_label.pack(side = tk.TOP, fill = tk.X, expand = False)

        self.m_listBox = tk.Listbox(self.m_chord, selectmode = tk.EXTENDED)
        self.m_listBox.pack(side = tk.TOP, fill = tk.X, expand = False, padx = 5, pady = 5)

        self.m_folderButton = ttk.Button(self.m_chord,text="Select folder",command = self.selectFolder)
        self.m_folderButton.pack(side = tk.TOP, fill = tk.X, expand = False)

class InvertTPDData(ProcessingStepControls):
    def __init__(self):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)")

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "First graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Second graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Third graph", bg="white"))
        # self.tab1 = MPLContainer(self.m_notebook, bg="white")
        # self.tab2 = ttk.Frame(self.m_notebook)
        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)
        # self.m_notebook.add(self.tab1,text="first")
        # self.m_notebook.add(self.tab2,text="second")
        # self.m_notebook.pack(expand=1,fill='both')
        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)
        tk.Label(self.m_chord, text='hello world, I am different!', bg='white').pack()



class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.ControlArray = []
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        self.ControlArray.append(ProcessTPDData())
        self.ControlArray.append(InvertTPDData())

        self.plotsFrame = PlotsFrame(self, bg ='white')
        self.controlsFrame = ControlsFrame(self, bg = 'grey')
        
        for c in self.ControlArray:
            c.initNotebook(self.plotsFrame)
            c.initChordUI(self.controlsFrame.accordion)

        self.controlsFrame.initChords([c.m_chord for c in self.ControlArray])

        self.resizeTimer = datetime.now()
        # self.rightFrame.resizeTest()
        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()
    # def resizePlots(self):
    #     self.rightFrame.resizeTest()

    def resetResizeTime(self,*args,**kwargs):
        # if( (not (self.lastWidth == self.winfo_width)) or (not (self.lastHeight == self.winfo_height))):
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

