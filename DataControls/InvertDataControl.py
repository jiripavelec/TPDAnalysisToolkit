import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer # pylint: disable=import-error
from DataControls.ControlElements import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, EnhancedEntry, DisplayOptionsFrame #ui element # pylint: disable=import-error
from tkinter.filedialog import askopenfilename
from DataModels.ProcessedDataWrapper import ProcessedDataWrapper # pylint: disable=import-error
from tkinter.filedialog import asksaveasfilename
from datetime import datetime
import math
import multiprocessing

class InvertDataControl(ProcessingStepControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Inversion Analysis", controller, accordion)
        self.m_parsedData = None
        self.m_prefactors = []
        self.m_inputFilePath = None

        self.m_plots["Input Data"] = MPLContainer(self.m_chord.m_notebookRef, "Input Data", "Desorption Rate (arb. U.)", "Temperature (K)", root)
        self.m_plots["Coverage vs. Temp."] = MPLContainer(self.m_chord.m_notebookRef, "Coverage vs. Temp.", "Coverage", "Temperature (K)", root)
        self.m_plots["Energy vs. Coverage"] = MPLContainer(self.m_chord.m_notebookRef, "Energy vs. Coverage", "Energy (eV)", "Coverage", root)
        self.m_plots["Sim. Coverage vs Temp."] = MPLContainer(self.m_chord.m_notebookRef, "Sim. Coverage vs Temp.", "Coverge (ML)", "Temperature (K)", root)
        self.m_plots["Sim. Desorption Rate vs Coverage"] = MPLContainer(self.m_chord.m_notebookRef, "Sim. Desorption Rate vs Coverage", "Desorption Rate (ML/K)", "Coverage", root)
        self.m_plots["Chi Squared vs Prefactor"] = MPLContainer(self.m_chord.m_notebookRef, "Chi Squared vs Prefactor", "Chi Squared Value", "Prefactor", root)

    def selectFile(self):
        buffer = askopenfilename(defaultextension=".pdat", filetypes=[('Processed Data','*.pdat'), ('All files','*.*')])
        if (not buffer == None): #we only want a new filepath if it is a valid path
            self.m_inputFilePath = buffer
            substrings = self.m_inputFilePath.split('/')
            self.m_inputFileName = substrings[len(substrings) - 1]
            self.m_fileNameLabel.configure(text = self.m_inputFileName)

    def checkInput(self):
        if(self.m_inputFilePath == None): #check for file selection
            tk.messagebox.showerror("Input File", "Please select a preprocssed file on which to perform the inversion analysis.")
            return False

        if(self.m_RBVariable.get() == 0): #single prefactor
            try:
                float(self.m_tPrefactorEntry.get())
            except ValueError:
                tk.messagebox.showerror("Prefactor Value", "Please enter a float for the prefactor. For example 1e17.")
                return False

        else: #prefactor range
            try: #prefactor start
                float(self.m_tPrefactorStartEntry.get())
            except ValueError:
                tk.messagebox.showerror("Lowest Prefactor", "Please enter a float for the lowest prefactor. For example 1e13.")
                return False

            try: #prefactor end
                float(self.m_tPrefactorEndEntry.get())
            except ValueError:
                tk.messagebox.showerror("Highest Prefactor", "Please enter a float for the highest prefactor. For example 1e21.")
                return False

            currentEntry = float(self.m_tPrefactorStartEntry.get())
            lastEntry = float(self.m_tPrefactorEndEntry.get())
            
            if(self.m_RBVariable.get() == 1): #linear range
                try: #prefactor end
                    float(self.m_tPrefactorIncrementEntry.get())
                except ValueError:
                    tk.messagebox.showerror("Increment", "Please enter a float for the prefactor increment.")
                    return False

                incrementEntry = float(self.m_tPrefactorIncrementEntry.get())
                if((lastEntry - currentEntry)/incrementEntry > 20):
                    tk.messagebox.showerror("Number of Data Points", "Too many simulated data points required. Adapt range so that less than 20 simulations are necessary per spectrum.")
                    # raise ValueError #ridiculous amount of data points

            else: #multiplicative range
                if(math.log10(lastEntry) - math.log10(currentEntry) > 20):
                    tk.messagebox.showerror("Number of Data Points", "Too many simulated data points required. Adapt range so that less than 20 simulations are necessary per spectrum.")
                    # raise ValueError #ridiculous amount of data points

        return True

    def processInput(self):
        if(not self.checkInput()): return
        self.m_invertedData = None
        
        if (not self.m_inputFilePath == None):
            self.m_parsedData = ProcessedDataWrapper(self.m_inputFilePath)
            if(not self.m_parsedData.parseProcessedDataFile()):
                tk.messagebox.showerror("Input File", "Please use an input file with normalized coverages!")
                return
            if(not self.m_parsedData.m_normalized):
                return #need a normalized monolayer coverage for inversion + simulation to make sense
            # self.m_parsedData.clearInvertedData() #incase we are reusing the wrapper
            # for c in self.m_plots:
            #     c.clearPlots()
            if(self.m_RBVariable.get() == 0): #single prefactor
                self.m_prefactors = ["{:e}".format(float(self.m_tPrefactorEntry.get()))]
            elif(self.m_RBVariable.get() == 1): #linear range
                currentEntry = float(self.m_tPrefactorStartEntry.get())
                lastEntry = float(self.m_tPrefactorEndEntry.get())
                incrementEntry = float(self.m_tPrefactorIncrementEntry.get())
                self.m_prefactors = []
                while(currentEntry <= lastEntry):
                    self.m_prefactors.append("{:e}".format(currentEntry))
                    currentEntry += incrementEntry #increase by order of magnitude
            else: #multiplicative range
                currentEntry = float(self.m_tPrefactorStartEntry.get())
                lastEntry = float(self.m_tPrefactorEndEntry.get())
                self.m_prefactors = []
                while(currentEntry <= lastEntry):
                    self.m_prefactors.append("{:e}".format(currentEntry))
                    currentEntry *= 10.0 #increase by order of magnitude
            
            for p in self.m_prefactors:
                self.m_parsedData.invertProcessedData(float(p)) #do the calculations

            self.m_parsedData.simulateCoveragesFromInvertedData()
            self.m_parsedData.evaluateData()

            #plot chi-squared value vs prefactor for all input coverages
            self.m_plots["Chi Squared vs Prefactor"].clearPlots()
            self.m_plots["Chi Squared vs Prefactor"].addPrimaryLinePlots(self.m_parsedData.getChiSquaredVSPrefactor(),self.m_parsedData.getCoverageLabels(),logXAxis = True)#, logYAxis = True)

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
            self.m_plots["Input Data"].clearPlots()
            self.m_plots["Input Data"].addPrimaryLinePlots(self.m_parsedData.getInputData(),self.m_parsedData.getCoverageLabels())
            #plot coverage vs temperature from experimental data
            self.m_plots["Coverage vs. Temp."].clearPlots()
            self.m_plots["Coverage vs. Temp."].addPrimaryLinePlots(self.m_parsedData.getExpCoverageVSTemp(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels())
            #plot desorption energy vs coverage from experimental data
            self.m_plots["Energy vs. Coverage"].clearPlots()
            for e,lbl in zip(self.m_parsedData.getDesEnergyVSCoverageList(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels()):
                self.m_plots["Energy vs. Coverage"].addPrimaryLinePlots(e,lbl)
            #plot simulated coverage vs temperature
            self.m_plots["Sim. Coverage vs Temp."].clearPlots()
            # self.m_plots[3].addLinePlots(self.m_parsedData.getExpDesorptionRateVSTemp())
            self.m_plots["Sim. Coverage vs Temp."].addPrimaryLinePlots(self.m_parsedData.getSimCoverageVSTemp(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels())
            #plot simulated desorption rate vs temperature
            self.m_plots["Sim. Desorption Rate vs Coverage"].clearPlots()
            self.m_plots["Sim. Desorption Rate vs Coverage"].addPrimaryLinePlots(self.m_parsedData.getSimDesRateVSTemp(float(selectedPrefactor)),self.m_parsedData.getCoverageLabels())  

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

    def toggleMarkers(self):
        for c in self.m_plots:
            c.toggleMarkers()

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



    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        # File selection

        self.m_inputLabel = ttk.Label(self.m_chordFrame, text='Input file:')
        self.m_inputLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_fileNameLabel = ttk.Label(self.m_chordFrame, text='No file selected')
        self.m_fileNameLabel.grid(row = 1, column = 1, columnspan = 3, sticky="nsew")

        self.m_selectButton = ttk.Button(self.m_chordFrame,text="Select File",command = self.selectFile)
        self.m_selectButton.grid(row=2, column = 2, columnspan=1, sticky = "nse")

        #Options

        self.m_optionsLabel = ttk.Label(self.m_chordFrame, text="Inversion Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        #Radiobutton var
        self.m_RBVariable = tk.IntVar(self.m_chordFrame)
        #Single Prefactor

        self.m_singleRB = ttk.Radiobutton(self.m_chordFrame, text ="Single Prefactor", variable = self.m_RBVariable,
            value = 0, command = self.changeRB)
        self.m_singleRB.grid(row=4, column = 1, sticky = "nsw")

        self.m_tPrefactorLabel = ttk.Label(self.m_chordFrame, text="Prefactor Value:")
        self.m_tPrefactorLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tPrefactorEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tPrefactorEntry.grid(row=5, column = 2, sticky = "nsw")

        #Or Prefactor Range

        self.m_linearRB = ttk.Radiobutton(self.m_chordFrame, text ="Prefactor Range - Linear", variable = self.m_RBVariable,
            value = 1, command = self.changeRB)
        self.m_linearRB.grid(row=6, column = 1, sticky = "nsw")

        self.m_tPrefactorIncrementLabel = ttk.Label(self.m_chordFrame, text="Increment:")
        self.m_tPrefactorIncrementLabel.grid(row=7, column = 1, sticky = "nse")

        self.m_tPrefactorIncrementEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tPrefactorIncrementEntry.grid(row=7, column = 2, sticky = "nsw")

        self.m_multiplicativeRB = ttk.Radiobutton(self.m_chordFrame, text ="Prefactor Range - Multiplicative (10x)", variable = self.m_RBVariable,
            value = 2, command = self.changeRB)
        self.m_multiplicativeRB.grid(row=8, column = 1, sticky = "nsw")

        self.m_tPrefactorStartLabel = ttk.Label(self.m_chordFrame, text="Lowest Prefactor:")
        self.m_tPrefactorStartLabel.grid(row=9, column = 1, sticky = "nse")

        self.m_tPrefactorStartEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tPrefactorStartEntry.grid(row=9, column = 2, sticky = "nsw")

        self.m_tPrefactorEndLabel = ttk.Label(self.m_chordFrame, text="Highest Prefactor:")
        self.m_tPrefactorEndLabel.grid(row=10, column = 1, sticky = "nse")

        self.m_tPrefactorEndEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tPrefactorEndEntry.grid(row=10, column = 2, sticky = "nsw")

        #default values

        self.m_tPrefactorStartEntry.setBackingVar("1e15")
        self.m_tPrefactorEndEntry.setBackingVar("1e17")

        self.m_RBVariable.set(2)
        self.changeRB()

        #Process Button

        self.m_processButton = ttk.Button(self.m_chordFrame, text = "Process Input", command = self.processInput)
        self.m_processButton.grid(row=11, column = 1, columnspan=2, sticky = "nsew")

        # self.m_prbar = ttk.Progressbar(self.m_chordFrame, orient ="horizontal", mode ="determinate", length = 50) #int(self.m_chordFrame.winfo_width() / 2))
        # self.m_prbar.grid(row = 12, column = 1, columnspan = 2, sticky="nsw")
        # self.m_prbar["value"] = 10  

        #Display options

        self.m_displayOptionsLabel = ttk.Label(self.m_chordFrame, text='Display Options:')
        self.m_displayOptionsLabel.grid(row = 12, column = 0, columnspan = 2, sticky="nsw")

        self.m_toggleMarkersButton = ttk.Button(self.m_chordFrame, text = "Toggle Markers", command = self.toggleMarkers)
        self.m_toggleMarkersButton.grid(row=13, column = 1, columnspan=2, sticky = "nsew")

        self.m_prefactorCBLabel = ttk.Label(self.m_chordFrame, text='Select prefactor to display data for:')
        self.m_prefactorCBLabel.grid(row = 14, column = 1, columnspan = 2, sticky="nsw")

        self.m_prefactorCB = ttk.Combobox(self.m_chordFrame)
        self.m_prefactorCB.bind("<<ComboboxSelected>>", self.plotDataForSelectedPrefactor) #binding to event because CB does not have 'command' param
        self.m_prefactorCB.grid(row = 15, column = 1, columnspan = 2, sticky = "nsew")

        #Save Button

        self.m_saveDataButton = ttk.Button(self.m_chordFrame, text = "Save Inverted Data", command = self.saveData)
        self.m_saveDataButton.grid(row=16, column = 1, columnspan=2, sticky = "nsew")

        for child in self.m_chordFrame.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.m_chordFrame.grid_columnconfigure(index=0, weight=1)
        self.m_chordFrame.grid_columnconfigure(index=1, weight=1)
        self.m_chordFrame.grid_columnconfigure(index=2, weight=1)