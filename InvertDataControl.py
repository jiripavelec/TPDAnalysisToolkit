import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, EnhancedEntry, DisplayOptionsFrame #ui element
from tkinter.filedialog import askdirectory, askopenfilenames
from ProcessedDataWrapper import ProcessedDataWrapper

class InvertDataControl(ProcessingStepControlBase):
    def __init__(self, controller):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)", controller)

    def selectFiles(self):
        buffer = list(askopenfilenames())
        if not (len(buffer) == 0):
            self.m_filePaths = buffer.copy() #we don't want to use the same instance => .copy()
            self.m_fileList = list()
            self.m_filesListBox.clear()
            for p in self.m_filePaths:
                substrings = p.split('/')
                fName = substrings[len(substrings) - 1]
                self.m_fileList.insert(0,fName)
            
            [self.m_filesListBox.insert(0, f) for f in self.m_fileList]
            self.m_fileList.reverse()

    def deselectFiles(self):
        indices = list(self.m_filesListBox.curselection())
        indices.reverse()
        for i in indices:
            self.m_filesListBox.delete(i)
            self.m_filePaths.pop(i)
            self.m_fileList.pop(i)

    def useProcessedFiles(self):
        #grab processed data from processRawDataControl
        self.m_parsedData = [ProcessedDataWrapper(rd) for rd in self.m_controller.requestProcessedData()]
        self.m_fileList = [f.m_fileName for f in self.m_parsedData]
        self.m_filePaths = [f.m_filePath for f in self.m_parsedData]
        self.m_filesListBox.clear()
        [self.m_filesListBox.insert(0, f) for f in self.m_fileList]

    def processInput(self):
        self.m_invertedData = []
        for f in self.m_parsedData:
            if (not f.m_dataParsed):
                raise NotImplementedError #parse data only if necessary
            raise NotImplementedError #always invert data

    def changeRB(self):
        self.m_tPrefactorEntry.configure(state = 'disabled')
        self.m_tPrefactorIncrementEntry.configure(state = 'disabled')
        self.m_tPrefactorStartEntry.configure(state = 'disabled')
        self.m_tPrefactorEndEntry.configure(state = 'disabled')
        if(self.m_RBVariable.get() == 0): #single prefactor
            self.m_tPrefactorEntry.configure(state = 'normal')
        elif(self.m_RBVariable.get() == 1): #linear range
            self.m_tPrefactorIncrementEntry.configure(state = 'normal')
            self.m_tPrefactorStartEntry.configure(state = 'normal')
            self.m_tPrefactorEndEntry.configure(state = 'normal')
        else: #multiplicative range
            self.m_tPrefactorIncrementEntry.configure(state = 'disabled')
            self.m_tPrefactorStartEntry.configure(state = 'normal')
            self.m_tPrefactorEndEntry.configure(state = 'normal')
            

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "Input Data", "Desorption Rate", "Temperature (K)"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Coverage vs. Temperature", "Coverage", "Temperature (K)"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Energy vs. Coverage", "Energy (eV)", "Coverage"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parentAccordion):
        self.m_chord = Chord(parentAccordion, self.m_notebook, title=self.m_title)

        # File selection

        self.m_filesListBoxLabel = ttk.Label(self.m_chord, text='Input files:')
        self.m_filesListBoxLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_filesListBox = ScrolledListBox(self.m_chord)
        self.m_filesListBox.grid(row = 1, column = 0, columnspan = 4, sticky = "nsew")

        self.m_fileButtonFrame = ttk.Frame(self.m_chord)
        self.m_fileButtonFrame.grid(row=2, column = 0, columnspan = 3, sticky = "nsew")

        self.m_selectButton = ttk.Button(self.m_fileButtonFrame,text="Select Files",command = self.selectFiles)
        self.m_selectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove Selected",command = self.deselectFiles)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_useProcessedButton = ttk.Button(self.m_fileButtonFrame,text="Use Data from Previous Step",command = self.useProcessedFiles)
        self.m_useProcessedButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        #Options

        self.m_optionsLabel = ttk.Label(self.m_chord, text="Inversion Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        #Radiobutton var
        self.m_RBVariable = tk.IntVar(self.m_chord)
        #Single Prefactor

        self.m_singleRB = ttk.Radiobutton(self.m_chord, text ="Single Prefactor", variable = self.m_RBVariable,
            value = 0, command = self.changeRB)
        self.m_singleRB.grid(row=4, column = 1, sticky = "nsw")

        self.m_tPrefactorLabel = ttk.Label(self.m_chord, text="Prefactor Value:")
        self.m_tPrefactorLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tPrefactorEntry = EnhancedEntry(self.m_chord)
        self.m_tPrefactorEntry.grid(row=5, column = 2, sticky = "nsw")

        #Or Prefactor Range

        self.m_linearRB = ttk.Radiobutton(self.m_chord, text ="Prefactor Range - Linear", variable = self.m_RBVariable,
            value = 1, command = self.changeRB)
        self.m_linearRB.grid(row=6, column = 1, sticky = "nsw")

        self.m_tPrefactorIncrementLabel = ttk.Label(self.m_chord, text="Increment:")
        self.m_tPrefactorIncrementLabel.grid(row=7, column = 1, sticky = "nse")

        self.m_tPrefactorIncrementEntry = EnhancedEntry(self.m_chord)
        self.m_tPrefactorIncrementEntry.grid(row=7, column = 2, sticky = "nsw")

        self.m_multiplicativeRB = ttk.Radiobutton(self.m_chord, text ="Prefactor Range - Multiplicative (10x)", variable = self.m_RBVariable,
            value = 2, command = self.changeRB)
        self.m_multiplicativeRB.grid(row=8, column = 1, sticky = "nsw")

        self.m_tPrefactorStartLabel = ttk.Label(self.m_chord, text="Lowest Prefactor:")
        self.m_tPrefactorStartLabel.grid(row=9, column = 1, sticky = "nse")

        self.m_tPrefactorStartEntry = EnhancedEntry(self.m_chord)
        self.m_tPrefactorStartEntry.grid(row=9, column = 2, sticky = "nsw")

        self.m_tPrefactorEndLabel = ttk.Label(self.m_chord, text="Highest Prefactor:")
        self.m_tPrefactorEndLabel.grid(row=10, column = 1, sticky = "nse")

        self.m_tPrefactorEndEntry = EnhancedEntry(self.m_chord)
        self.m_tPrefactorEndEntry.grid(row=10, column = 2, sticky = "nsw")

        self.m_RBVariable.set(2)
        self.changeRB()

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

        self.m_chord.grid_columnconfigure(index=0, weight=1)
        self.m_chord.grid_columnconfigure(index=1, weight=1)
        self.m_chord.grid_columnconfigure(index=2, weight=1)