import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, EnhancedEntry, DisplayOptionsFrame #ui element
from tkinter.filedialog import askopenfilename
from ProcessedDataWrapper import ProcessedDataWrapper
from tkinter.filedialog import asksaveasfilename
from datetime import datetime
import math
import multiprocessing

class InvertDataControl(ProcessingStepControlBase):
    def __init__(self, controller):
        super().__init__("Inversion Analysis", controller)
        self.m_parsedData = None
        self.m_prefactors = []
        self.m_inputFilePath = None

    def selectFile(self):
        buffer = askopenfilename(defaultextension=".pdat", filetypes=[('Processed Data','*.pdat'), ('All files','*.*')])
        if (not buffer == None): #we only want a new filepath if it is a valid path
            self.m_inputFilePath = buffer
            substrings = self.m_inputFilePath.split('/')
            self.m_inputFileName = substrings[len(substrings) - 1]
            self.m_fileNameLabel.configure(text = self.m_inputFileName)

    def checkInput(self):
        if(self.m_inputFilePath == None): #check for file selection
            tk.messagebox.showerror("Input Files", "Please select a file to process.")
            return False

        # try:
        #     int(self.m_tCutStartEntry.get())
        # except ValueError:
        #     tk.messagebox.showerror("Cut Data Start Temp", "Please enter an integer for the temperature at which to start cutting data.")
        #     return False

        # try:
        #     int(self.m_tCutEndEntry.get())
        # except ValueError:
        #     tk.messagebox.showerror("Cut Data End Temp", "Please enter an integer for the temperature at which to stop cutting data.")
        #     return False

        # try: #check for tCutStart
        #     int(self.m_tRampStartEntry.get())
        # except ValueError:
        #     tk.messagebox.showerror("Ramp Start Temp", "Please enter an integer for a temperature slightly beyond the start of the linear temperature ramp.")
        #     return False

        # try: #check for tCutEnd
        #     int(self.m_tRampEndEntry.get())
        # except ValueError:
        #     tk.messagebox.showerror("Remp End Temp", "Please enter an integer for a temperature slightly before the end of the linear temperature ramp.")
        #     return False
        
        return True

    def processInput(self):
        self.m_invertedData = None
        #TODO: input checking + highlighting of incorrect entries
        if (not self.m_inputFilePath == None):
            self.m_parsedData = ProcessedDataWrapper(self.m_inputFilePath)
            self.m_parsedData.parseProcessedDataFile()
            if(not self.m_parsedData.m_normalized):
                return #need a normalized monolayer coverage for inversion + simulation to make sense
            # self.m_parsedData.clearInvertedData() #incase we are reusing the wrapper
            for c in self.mplContainers:
                c.clearPlots()
            if(self.m_RBVariable.get() == 0): #single prefactor
                self.m_prefactors = ["{:e}".format(float(self.m_tPrefactorEntry.get()))]
            elif(self.m_RBVariable.get() == 1): #linear range
                currentEntry = float(self.m_tPrefactorStartEntry.get())
                lastEntry = float(self.m_tPrefactorEndEntry.get())
                incrementEntry = float(self.m_tPrefactorIncrementEntry.get())
                if((lastEntry - currentEntry)/incrementEntry > 20):
                    raise ValueError #ridiculous amount of data points
                self.m_prefactors = []
                while(currentEntry <= lastEntry):
                    self.m_prefactors.append("{:e}".format(currentEntry))
                    currentEntry += incrementEntry #increase by order of magnitude
            else: #multiplicative range
                currentEntry = float(self.m_tPrefactorStartEntry.get())
                lastEntry = float(self.m_tPrefactorEndEntry.get())
                if(math.log(lastEntry) - math.log(currentEntry) > 20):
                    raise ValueError #ridiculous amount of data points
                self.m_prefactors = []
                while(currentEntry <= lastEntry):
                    self.m_prefactors.append("{:e}".format(currentEntry))
                    currentEntry *= 10.0 #increase by order of magnitude

            # if( len(self.m_prefactors) == 1): #only one prefactor
            #     self.m_parsedData.invertProcessedData(float(self.m_prefactors[0])) #do the calculations
            # else: #try multiprocessing
            #     cpu_count = multiprocessing.cpu_count()
            #     if( cpu_count == 1): #single-core
            #         for p in self.m_prefactors:
            #             self.m_parsedData.invertProcessedData(float(p)) #do the calculations
            #     else: #try using as many cores as there are prefactors, or at least as many cores as we have (minus one for UI thread)
            #         with multiprocessing.Pool(min(cpu_count - 1,len(self.m_prefactors))) as p:
            #             p.map(self.m_parsedData.invertProcessedData, [float(p) for p in self.m_prefactors])
            
            for p in self.m_prefactors:
                self.m_parsedData.invertProcessedData(float(p)) #do the calculations

            self.m_parsedData.simulateCoveragesFromInvertedData()
            self.m_parsedData.evaluateData()

            #plot chi-squared value vs prefactor for all input coverages
            self.mplContainers[5].clearPlots()
            self.mplContainers[5].addLinePlots(self.m_parsedData.getChiSquaredVSPrefactor(),self.m_parsedData.getCoverageLabels(),logXAxis = True, logYAxis = True)

            self.m_prefactorCB["values"] = self.m_prefactors
            self.plotDataForSelectedPrefactor()
            
    def plotDataForSelectedPrefactor(self,*args,**kwargs):
        if(len(self.m_prefactors) == 0):
            return
        else:
            selectedPrefactor = self.m_prefactorCB.get()
            if(selectedPrefactor == ''):
                self.m_prefactorCB.current(0) #set to first entry
                selectedPrefactor = self.m_prefactorCB.get()

            #plot input data
            self.mplContainers[0].clearPlots()
            self.mplContainers[0].addLinePlots(self.m_parsedData.getInputData(),self.m_parsedData.getCoverageLabels())
            #plot coverage vs temperature from experimental data
            self.mplContainers[1].clearPlots()
            self.mplContainers[1].addLinePlots(self.m_parsedData.getExpCoverageVSTemp(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels())
            #plot desorption energy vs coverage from experimental data
            self.mplContainers[2].clearPlots()
            for e,lbl in zip(self.m_parsedData.getDesEnergyVSCoverageList(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels()):
                self.mplContainers[2].addLinePlots(e,lbl)
            #plot simulated coverage vs temperature
            self.mplContainers[3].clearPlots()
            # self.mplContainers[3].addLinePlots(self.m_parsedData.getExpDesorptionRateVSTemp())
            self.mplContainers[3].addLinePlots(self.m_parsedData.getSimCoverageVSTemp(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels())
            #plot simulated desorption rate vs temperature
            self.mplContainers[4].clearPlots()
            self.mplContainers[4].addLinePlots(self.m_parsedData.getSimDesRateVSTemp(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels())
            

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
        if (self.m_parsedData == None):
            return
        outputFilePath = asksaveasfilename()
        substrings = outputFilePath.split('/')
        #consider using s = '/' result = s.join(substrings[x:y])
        outputFilePath = substrings[0]
        for s in substrings[1:-1]:
            outputFilePath = outputFilePath + '/' + s
        substrings = substrings[-1].split('.')
        fileName = substrings[0]
        if(len(substrings) > 1):
            for s in substrings[1:-1]:
                fileName = fileName + '.' + s
        # dateTimeString = str(datetime.now()).replace('-','').replace(' ', '_').replace(':','')
        # fileName = fileName + '.' + dateTimeString
        outputFilePath = outputFilePath + '/' + fileName
        self.m_parsedData.saveInvertedDataToFile(outputFilePath)


    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "Input Data", "Desorption Rate (arb. U.)", "Temperature (K)"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Coverage vs. Temperature", "Coverage", "Temperature (K)"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Energy vs. Coverage", "Energy (eV)", "Coverage"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Simulated Coverage vs Temperature", "Coverge (ML)", "Temperature (K)"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Simulated Desorption Rate vs Coverage", "Desorption Rate (ML/K)", "Coverage"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Chi Squared vs Prefactor", "Chi Squared Value", "Prefactor"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parentAccordion):
        self.m_chordContainer = Chord(parentAccordion, self.m_notebook, title=self.m_title)
        self.m_chord = self.m_chordContainer.m_scrollable_frame

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

        #default values

        self.m_tPrefactorStartEntry.setBackingVar("1e15")
        self.m_tPrefactorEndEntry.setBackingVar("1e17")

        self.m_RBVariable.set(2)
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