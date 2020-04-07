import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from tkinter.filedialog import askdirectory, askopenfilenames


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


    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "Raw Data", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Processed Data", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)

        self.m_filesListBoxLabel = ttk.Label(self.m_chord, text='Input files:')
        self.m_filesListBoxLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_filesListBox = ScrolledListBox(self.m_chord)
        self.m_filesListBox.grid(row = 1, column = 0, columnspan = 4, sticky = "nsew")

        # self.m_directoryLabel = tk.Label(self.m_chord, text='No directory selected')
        # self.m_directoryLabel = tk.Entry(self.m_chord, textvariable = self.m_filesDirectory, state = tk.DISABLED)
        # self.m_directoryLabel.grid(row = 2, column = 0, columnspan = 2, sticky="nsw", padx = 3, pady = 3)

        self.m_fileButtonFrame = ttk.Frame(self.m_chord)
        self.m_fileButtonFrame.grid(row=2, column = 0, columnspan = 4, sticky = "nsew")

        self.m_selectButton = ttk.Button(self.m_fileButtonFrame,text="Select files",command = self.selectFiles)
        # self.m_selectButton.grid(row=2, column = 2, sticky = "nsew", padx = 3, pady = 3)
        self.m_selectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)
        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove selected",command = self.deselectFiles)
        # self.m_deselectButton.grid(row=2, column = 1, sticky = "nsew", padx = 3, pady = 3)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_optionsLabel = ttk.Label(self.m_chord, text="Processing options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        self.m_tStartLabel = ttk.Label(self.m_chord, text="Starting temp.:")
        self.m_tStartLabel.grid(row=4, column = 1, sticky = "nse")

        self.m_tStart = ""
        self.m_tStartEntry = ttk.Entry(self.m_chord, textvariable = self.m_tStart)
        self.m_tStartEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tEndLabel = ttk.Label(self.m_chord, text="Final temp.:")
        self.m_tEndLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tEnd = ""
        self.m_tEndEntry = ttk.Entry(self.m_chord, textvariable = self.m_tEnd)
        self.m_tEndEntry.grid(row=5, column = 2, sticky = "nsw")

        self.m_smoothCB = EnhancedCheckButton(self.m_chord, text="Smooth")
        self.m_smoothCB.grid(row = 6, column = 1, sticky = "nsw")

        self.m_removeBackgroundCB = EnhancedCheckButton(self.m_chord, text="Remove Background")
        self.m_removeBackgroundCB.grid(row = 6, column = 2, sticky = "nsw")

        self.m_normalizeCB = EnhancedCheckButton(self.m_chord, text = "Normalize")
        self.m_normalizeCB.grid(row = 7, column = 1, sticky = "nsw")

        self.m_subtractCB = EnhancedCheckButton(self.m_chord, text = "Subtract Spectrum", command=self.toggleSubtractCB)
        self.m_subtractCB.grid(row = 7, column = 2, sticky = "nsw")

        self.m_subtractSelection = ttk.Combobox(self.m_chord, state = tk.DISABLED)
        self.m_subtractSelection.grid(row=8, column=1, columnspan=2, sticky= "nsew")

        self.m_processButton = ttk.Button(self.m_chord, text = "Process input", command = self.processInput)
        self.m_processButton.grid(row=9, column = 2, columnspan=2, sticky = "nsew")

        for child in self.m_chord.winfo_children():
            child.grid_configure(padx=3, pady=3)

        for child in self.m_fileButtonFrame.winfo_children():
            child.pack_configure(padx=3, pady=3)

        self.m_chord.grid_columnconfigure(index=0, weight=1)
        self.m_chord.grid_columnconfigure(index=1, weight=1)
        self.m_chord.grid_columnconfigure(index=2, weight=1)
        self.m_chord.grid_columnconfigure(index=3, weight=1)
