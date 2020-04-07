import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, DisplayOptionsFrame #ui element
from tkinter.filedialog import askdirectory, askopenfilenames
from ProcessRawDataFunction import RawDataWrapper


class ProcessRawDataControl(ProcessingStepControlBase):
    def __init__(self, bg):
        super().__init__("Process TPD Data")
        # self.m_filesDirectory = ""

    def selectFiles(self):
        # self.m_filesDirectory = askdirectory()
        self.m_filePaths = list(askopenfilenames())
        self.m_fileList = list()
        self.m_filesListBox.clear()
        for p in self.m_filePaths:
            substrings = p.split('/')
            fName = substrings[len(substrings) - 1]
            self.m_fileList.insert(0,fName)
        
        [self.m_filesListBox.insert(0, f) for f in self.m_fileList]
        self.m_fileList.reverse()
        self.m_subtractSelection["values"] = self.m_fileList


        # for i in range(len(self.m_filePaths)):
        #     print(self.m_filesListBox.get(i) + " " + self.m_filePaths[i])
        # for (a,b) in zip(self.m_filesListBox.get(0, self.m_filesListBox.size() - 1), self.m_filePaths):

    def deselectFiles(self):
        indices = list(self.m_filesListBox.curselection())
        indices.reverse()
        for i in indices:
            self.m_filesListBox.delete(i)
            self.m_filePaths.pop(i)
            self.m_fileList.pop(i)
        self.m_subtractSelection["values"] = self.m_fileList

        # for i in range(len(self.m_filePaths)):
        #     print(self.m_filePaths[i] + " " + self.m_filesListBox.get(i))

    def toggleSubtractCB(self):
        if(self.m_subtractCB.get() == 0):
            self.m_subtractSelection.configure(state = tk.DISABLED)
        else:
            self.m_subtractSelection.configure(state = tk.NORMAL)

    def plotSelectedMasses(self):
        for c in self.mplContainers:
            c.clearPlots()

        for d in self.m_parsedData:
            self.mplContainers[0].addLinePlots(d.getRawData(self.m_massDisplayOptions.getMassesToDisplay()))
            self.mplContainers[1].addLinePlots(d.getProcessedData(self.m_massDisplayOptions.getMassesToDisplay()))

    def processInput(self):
        self.m_parsedData = []
        for f in self.m_filePaths:
            wrapper = RawDataWrapper(f,150,450,100,600,0.1,[28,29])
            wrapper.parseRawDataFile()
            self.m_parsedData.append(wrapper)

        self.m_massDisplayOptions.resetMasses(self.m_parsedData)
        self.plotSelectedMasses()

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)
        self.mplContainers.append(MPLContainer(self.m_notebook, "Raw Data", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Processed Data", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)

        # File selection

        self.m_filesListBoxLabel = ttk.Label(self.m_chord, text='Input files:')
        self.m_filesListBoxLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_filesListBox = ScrolledListBox(self.m_chord)
        self.m_filesListBox.grid(row = 1, column = 0, columnspan = 4, sticky = "nsew")

        # self.m_directoryLabel = tk.Label(self.m_chord, text='No directory selected')
        # self.m_directoryLabel = tk.Entry(self.m_chord, textvariable = self.m_filesDirectory, state = tk.DISABLED)
        # self.m_directoryLabel.grid(row = 2, column = 0, columnspan = 2, sticky="nsw", padx = 3, pady = 3)

        self.m_fileButtonFrame = ttk.Frame(self.m_chord)
        self.m_fileButtonFrame.grid(row=2, column = 0, columnspan = 3, sticky = "nsew")

        self.m_selectButton = ttk.Button(self.m_fileButtonFrame,text="Select Files",command = self.selectFiles)
        self.m_selectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove Selected",command = self.deselectFiles)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        # Options from here onwards

        self.m_optionsLabel = ttk.Label(self.m_chord, text="Processing Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chord, text="Cut Data Starting Temp.:")
        self.m_tCutStartLabel.grid(row=4, column = 1, sticky = "nse")

        self.m_tCutStart = ""
        self.m_tCutStartEntry = ttk.Entry(self.m_chord, textvariable = self.m_tCutStart)
        self.m_tCutStartEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chord, text="Cut Data End Temp.:")
        self.m_tCutEndLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tCutEnd = ""
        self.m_tCutEndEntry = ttk.Entry(self.m_chord, textvariable = self.m_tCutEnd)
        self.m_tCutEndEntry.grid(row=5, column = 2, sticky = "nsw")

        self.m_tRampStartLabel = ttk.Label(self.m_chord, text="Ramp Starting Temp.:")
        self.m_tRampStartLabel.grid(row=6, column = 1, sticky = "nse")

        self.m_tRampStart = ""
        self.m_tRampStartEntry = ttk.Entry(self.m_chord, textvariable = self.m_tRampStart)
        self.m_tRampStartEntry.grid(row=6, column = 2, sticky = "nsw")

        self.m_tRampEndLabel = ttk.Label(self.m_chord, text="Ramp End Temp.:")
        self.m_tRampEndLabel.grid(row=7, column = 1, sticky = "nse")

        self.m_tRampEnd = ""
        self.m_tRampEndEntry = ttk.Entry(self.m_chord, textvariable = self.m_tRampEnd)
        self.m_tRampEndEntry.grid(row=7, column = 2, sticky = "nsw")

        # Checkbuttons

        self.m_smoothCB = EnhancedCheckButton(self.m_chord, text="Smooth")
        self.m_smoothCB.grid(row = 8, column = 1, sticky = "nsw")

        self.m_removeBackgroundCB = EnhancedCheckButton(self.m_chord, text="Remove Background")
        self.m_removeBackgroundCB.grid(row = 8, column = 2, sticky = "nsw")

        self.m_normalizeCB = EnhancedCheckButton(self.m_chord, text = "Normalize")
        self.m_normalizeCB.grid(row = 9, column = 1, sticky = "nsw")

        self.m_subtractCB = EnhancedCheckButton(self.m_chord, text = "Subtract Spectrum", command=self.toggleSubtractCB)
        self.m_subtractCB.grid(row = 9, column = 2, sticky = "nsw")

        # Combobox

        self.m_subtractSelection = ttk.Combobox(self.m_chord, state = tk.DISABLED)
        self.m_subtractSelection.grid(row=10, column=1, columnspan=2, sticky= "nsew")

        #Process Button

        self.m_processButton = ttk.Button(self.m_chord, text = "Process Input", command = self.processInput)
        self.m_processButton.grid(row=11, column = 1, columnspan=2, sticky = "nse")

        #Display options

        self.m_displayOptionsLabel = ttk.Label(self.m_chord, text='Display Options')
        self.m_displayOptionsLabel.grid(row = 12, column = 0, columnspan = 2, sticky="nsw")

        self.m_massDisplayOptions = DisplayOptionsFrame(self.m_chord, self.plotSelectedMasses)
        self.m_massDisplayOptions.grid(row = 13, column = 1, columnspan = 2, sticky = "nsw")

        self.m_massDisplayOptions.m_availableMassesListBox

        for child in self.m_chord.winfo_children():
            child.grid_configure(padx=3, pady=3)

        for child in self.m_fileButtonFrame.winfo_children():
            child.pack_configure(padx=3, pady=3)

        for child in self.m_massDisplayOptions.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.m_chord.grid_columnconfigure(index=0, weight=1)
        self.m_chord.grid_columnconfigure(index=1, weight=1)
        self.m_chord.grid_columnconfigure(index=2, weight=1)
        # self.m_chord.grid_columnconfigure(index=3, weight=1)
