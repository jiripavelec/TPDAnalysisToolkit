import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, EnhancedEntry, DisplayOptionsFrame #ui element
from tkinter.filedialog import askopenfilename
from ProcessedDataWrapper import ProcessedDataWrapper

class InvertDataControl(ProcessingStepControlBase):
    def __init__(self, controller):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)", controller)
        self.m_parsedData = None
        self.m_prefactors = []

    def selectFile(self):
        buffer = askopenfilename(defaultextension=".pdat")
        if (not buffer == None): #we only want a new filepath if it is a valid path
            self.m_inputFilePath = buffer
            substrings = self.m_inputFilePath.split('/')
            self.m_inputFileName = substrings[len(substrings) - 1]
            self.m_fileNameLabel.configure(text = self.m_inputFileName)

    def processInput(self):
        self.m_invertedData = None
        #TODO: input checking + highlighting of incorrect entries
        if (not self.m_inputFilePath == None):
            self.m_parsedData = ProcessedDataWrapper(self.m_inputFilePath)
            self.m_parsedData.parseProcessedDataFile()
            self.m_parsedData.clearInvertedData() #incase we are reusing the wrapper
            for c in self.mplContainers:
                c.clearPlots()
            if(self.m_RBVariable.get() == 0): #single prefactor
                self.m_prefactors = ["{:e}".format(float(self.m_tPrefactorEntry.get()))]
            elif(self.m_RBVariable.get() == 1): #linear range
                self.m_prefactors = []
                currentEntry = float(self.m_tPrefactorStartEntry.get())
                lastEntry = float(self.m_tPrefactorEndEntry.get())
                incrementEntry = float(self.m_tPrefactorIncrementEntry.get())
                while(currentEntry <= lastEntry):
                    self.m_prefactors.append("{:e}".format(currentEntry))
                    currentEntry += incrementEntry #increase by order of magnitude
            else: #multiplicative range
                self.m_prefactors = []
                currentEntry = float(self.m_tPrefactorStartEntry.get())
                lastEntry = float(self.m_tPrefactorEndEntry.get())
                while(currentEntry <= lastEntry):
                    self.m_prefactors.append("{:e}".format(currentEntry))
                    currentEntry *= 10.0 #increase by order of magnitude

            for p in self.m_prefactors:
                self.m_parsedData.invertProcessedData(float(p)) #do the calculations
            self.m_prefactorCB["values"] = self.m_prefactors
            self.plotDataForSelectedPrefactor()
            
    def plotDataForSelectedPrefactor(self,*args,**kwargs):
        if(len(self.m_prefactors) == 0):
            return
        else:
            selectedPrefactor = self.m_prefactorCB.get()
            if(selectedPrefactor == None):
                self.m_prefactorCB.current(0) #set to first entry
                selectedPrefactor = self.m_prefactorCB.get()
            for c in self.mplContainers:
                c.clearPlots()
            self.mplContainers[0].addLinePlots(self.m_parsedData.getInputData())
            self.mplContainers[1].addLinePlots(self.m_parsedData.getCoverageVSTemp(float(selectedPrefactor)))
            for e in self.m_parsedData.getDesEnergyVSCoverageList(float(selectedPrefactor)):
                self.mplContainers[2].addLinePlots(e)

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
            
    def saveData(self):
        raise NotImplementedError


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

        self.m_inputLabel = ttk.Label(self.m_chord, text='Input file:')
        self.m_inputLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_fileNameLabel = ttk.Label(self.m_chord, text='No file selected')
        self.m_fileNameLabel.grid(row = 1, column = 1, columnspan = 3, sticky="nsew")

        self.m_selectButton = ttk.Button(self.m_chord,text="Select File",command = self.selectFile)
        self.m_selectButton.grid(row=2, column = 2, columnspan=1, sticky = "nse")

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

        self.m_RBVariable.set(0)
        self.changeRB()

        #Process Button

        self.m_processButton = ttk.Button(self.m_chord, text = "Process Input", command = self.processInput)
        self.m_processButton.grid(row=11, column = 1, columnspan=2, sticky = "nsew")

        # self.m_prbar = ttk.Progressbar(self.m_chord, orient ="horizontal", mode ="determinate", length = 50) #int(self.m_chord.winfo_width() / 2))
        # self.m_prbar.grid(row = 12, column = 1, columnspan = 2, sticky="nsw")
        # self.m_prbar["value"] = 10  

        #Display options

        self.m_displayOptionsLabel = ttk.Label(self.m_chord, text='Display Options:')
        self.m_displayOptionsLabel.grid(row = 12, column = 0, columnspan = 2, sticky="nsw")

        self.m_prefactorCBLabel = ttk.Label(self.m_chord, text='Select prefactor to display data for:')
        self.m_prefactorCBLabel.grid(row = 13, column = 1, columnspan = 2, sticky="nsw")

        self.m_prefactorCB = ttk.Combobox(self.m_chord)
        self.m_prefactorCB.bind("<<ComboboxSelected>>", self.plotDataForSelectedPrefactor) #binding to event because CB does not have 'command' param
        self.m_prefactorCB.grid(row = 14, column = 1, columnspan = 2, sticky = "nsew")

        #Save Button

        self.m_saveDataButton = ttk.Button(self.m_chord, text = "Save Inverted Data", command = self.saveData)
        self.m_saveDataButton.grid(row=15, column = 1, columnspan=2, sticky = "nsew")

        for child in self.m_chord.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.m_chord.grid_columnconfigure(index=0, weight=1)
        self.m_chord.grid_columnconfigure(index=1, weight=1)
        self.m_chord.grid_columnconfigure(index=2, weight=1)