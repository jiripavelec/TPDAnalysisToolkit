import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import ControlsFrame, Chord, ScrolledListBox #ui element
from PlotsFrame import PlotsFrame, MPLContainer
from tkinter.filedialog import askdirectory, askopenfilenames
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

    #This is for the controls on the left side of the UI
    def initChordUI(self, parent):
        raise NotImplementedError()

    #This is for the tabs with plots on the right side of the UI
    def initNotebook(self, parent):
        raise NotImplementedError()

    #This is to reduce the update frequency of plot resizing to
    #a frequency lower than that of resize events from the main
    #window
    def setResizeTime(self):
        for c in self.mplContainers:
            c.resizeDateTime = datetime.now()

    def selectFiles(self):
        raise NotImplementedError()


class ProcessTPDData(ProcessingStepControls):
    def __init__(self):
        super().__init__("Process TPD Data")
        # self.m_filesDirectory = ""

    def selectFiles(self):
        # self.m_filesDirectory = askdirectory()
        self.m_filePaths = list(askopenfilenames())
        # self.m_fileList = []
        self.m_filesListBox.clear()
        for p in self.m_filePaths:
            substrings = p.split('/')
            fName = substrings[len(substrings) - 1]
            # self.m_fileList.insert(0,fName)
            self.m_filesListBox.insert(0, fName)
        self.m_filePaths.reverse()

        for i in range(len(self.m_filePaths)):
            print(self.m_filePaths[i] + " " + self.m_filesListBox.get(i))
        # for (a,b) in zip(self.m_filesListBox.get(0, self.m_filesListBox.size() - 1), self.m_filePaths):

    def deselectFiles(self):
        indices = list(self.m_filesListBox.curselection())
        indices.reverse()
        for i in indices:
            self.m_filesListBox.delete(i)
            self.m_filePaths.pop(i)

        for i in range(len(self.m_filePaths)):
            print(self.m_filePaths[i] + " " + self.m_filesListBox.get(i))


    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "Raw Data", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Processed Data", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)

        self.m_filesListBoxLabel = tk.Label(self.m_chord, text='Input files:')
        self.m_filesListBoxLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_filesListBox = ScrolledListBox(self.m_chord)
        self.m_filesListBox.grid(row = 1, column = 0, columnspan = 3, sticky = "nsew")

        # self.m_directoryLabel = tk.Label(self.m_chord, text='No directory selected')
        # self.m_directoryLabel = tk.Entry(self.m_chord, textvariable = self.m_filesDirectory, state = tk.DISABLED)
        # self.m_directoryLabel.grid(row = 2, column = 0, columnspan = 2, sticky="nsw", padx = 3, pady = 3)

        self.m_fileButtonFrame = tk.Frame(self.m_chord)
        self.m_fileButtonFrame.grid(row=2, column = 0, columnspan = 3, sticky = "nsew")

        self.m_selectButton = ttk.Button(self.m_fileButtonFrame,text="Select files",command = self.selectFiles)
        # self.m_selectButton.grid(row=2, column = 2, sticky = "nsew", padx = 3, pady = 3)
        self.m_selectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)
        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove selected",command = self.deselectFiles)
        # self.m_deselectButton.grid(row=2, column = 1, sticky = "nsew", padx = 3, pady = 3)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_optionsLabel = tk.Label(self.m_chord, text="Processing options")
        self.m_optionsLabel.grid(row=3, column = 0, sticky = "nsw")
        
        self.m_tStartLabel = tk.Label(self.m_chord, text="Starting temp.:")
        self.m_tStartLabel.grid(row=4, column = 1, sticky = "nsw")

        self.m_tStart = ""
        self.m_tStartEntry = tk.Entry(self.m_chord, textvariable = self.m_tStart)
        self.m_tStartEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tEndLabel = tk.Label(self.m_chord, text="Final temp.:")
        self.m_tEndLabel.grid(row=5, column = 1, sticky = "nsw")

        self.m_tEnd = ""
        self.m_tEndEntry = tk.Entry(self.m_chord, textvariable = self.m_tEnd)
        self.m_tEndEntry.grid(row=5, column = 2, sticky = "nsw")

        for child in self.m_chord.winfo_children():
            child.grid_configure(padx=3, pady=3)

        for child in self.m_fileButtonFrame.winfo_children():
            child.pack_configure(padx=3, pady=3)

        self.m_chord.grid_columnconfigure(index=0, weight=1)
        self.m_chord.grid_columnconfigure(index=1, weight=1)
        self.m_chord.grid_columnconfigure(index=2, weight=1)

class InvertTPDData(ProcessingStepControls):
    def __init__(self):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)")

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "First graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Second graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Third graph", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

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
        self.plotsFrame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        # self.plotsFrame.grid(row = 0, column = 1, sticky = "nsew")

        self.controlsFrame = ControlsFrame(self, bg = 'grey')
        self.controlsFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        # self.controlsFrame.grid(row = 0 , column = 0, sticky = "nsew")
        
        # self.grid_columnconfigure(index = 0, weight = 1)
        # self.grid_columnconfigure(index = 1, weight = 3)
        # self.grid_rowconfigure(index = 0, weight = 1)

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

