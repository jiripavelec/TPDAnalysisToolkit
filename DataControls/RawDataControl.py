import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from PlotsFrame import MPLContainer # pylint: disable=import-error
from DataControls.ControlElements import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingControlBase, DisplayOptionsFrame, EnhancedEntry, InputFileListBoxControl #ui elements # pylint: disable=import-error
from tkinter.filedialog import askdirectory, askopenfilenames, asksaveasfilename 
from DataModels.RawDataWrapper import RawDataWrapper # pylint: disable=import-error
import numpy as np
import os.path
from os import path, chdir
# from glob import glob

#This class is the control meant for manipulating raw data.
#It uses the RawDataWrapper as an interface to do so.
class RawDataControl(ProcessingControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Process TPD Data", controller, accordion)
        self.m_filePaths = []
        self.m_parsedData = []
        # self.m_notebook.bind("<<NotebookTabChanged>>", self.onNotebookTabChanged)
        # self.m_plots.append(MPLContainer(self.m_notebook, "Raw Data", "Desorption Rate", "Temperature (K)"))
        self.m_plots["Raw Data vs. Temp."] = MPLContainer(self.m_chord.m_notebookRef, "Raw Data vs. Temp.", "Desorption Rate", "Temperature (K)", root)
        self.m_plots["Raw Data vs. Time"] = MPLContainer(self.m_chord.m_notebookRef, "Raw Data vs. Time.", "Desorption Rate", "Time (ms)", root, secondaryYAxis=True,secondaryYAxisName="Temperature (K)", legendLoc='center right')
        self.m_plots["Processed Data"] = MPLContainer(self.m_chord.m_notebookRef, "Processed Data", "Desorption Rate", "Temperature (K)", root)
        self.m_plots["Log Plot (Processed)"] = MPLContainer(self.m_chord.m_notebookRef, "Log Plot (Processed)", "ln(Desorption Rate)", "Temperature (K)", root)
        self.m_plots["Arrhenius Plot (Processed)"] = MPLContainer(self.m_chord.m_notebookRef, "Arrhenius Plot (Processed)", "ln(Desorption Rate)", "Reciprocal Temperature (1/K)", root, invertXAxis=True)
        # self.m_plots["Temperature Ramp"] = MPLContainer(self.m_chord.m_notebookRef, "Temperature Ramp", "Temperature (K)", "Time (ms)", root)

    def onUpdateFileList(self, fileList):
        self.m_subtractSelection["values"] = fileList
        self.m_normSelection["values"] = fileList

    def toggleSubtractCB(self):
        if(self.m_subtractCB.instate(['!selected'])):
            self.m_subtractSelection.configure(state = tk.DISABLED)
        else:
            self.m_subtractSelection.configure(state = 'readonly')

    def toggleNormalizeCB(self):
        if(self.m_normalizeCB.instate(['!selected'])):
            self.m_removeBackgroundCB.configure(state = tk.NORMAL)
            self.m_normSelection.configure(state = tk.DISABLED)
        else:
            self.m_removeBackgroundCB.set(1) #if we want to normalize, we also have to remove the background, otherwise it does not make sense
            self.m_removeBackgroundCB.configure(state = tk.DISABLED)
            self.m_normSelection.configure(state = 'readonly')

    def toggleMarkers(self):
        for c in self.m_plots.values():
            c.toggleMarkers()

    def plotSelectedMasses(self):
        for c in self.m_plots.values():
            c.clearPlots()

        tempMasses = self.m_massDisplayOptions.getMassesToDisplay()
        if(len(tempMasses) == 0):
            return

        for d in self.m_parsedData:
            self.m_plots["Raw Data vs. Temp."].addPrimaryLinePlots(d.getRawDataVSRawTemp(tempMasses),d.getLangmuirLabels(tempMasses))
            self.m_plots["Raw Data vs. Time"].addPrimaryLinePlots(d.getRawDataVSRawTime(tempMasses),d.getLangmuirLabels(tempMasses))
            self.m_plots["Raw Data vs. Time"].addSecondaryLinePlots(d.getRawTempVSRawTime())
            self.m_plots["Processed Data"].addPrimaryLinePlots(d.getProcessedData(tempMasses),d.getCoverageLabels(tempMasses))
            self.m_plots["Log Plot (Processed)"].addPrimaryLinePlots(d.getProcessedLNData(tempMasses),d.getCoverageLabels(tempMasses))
            self.m_plots["Arrhenius Plot (Processed)"].addPrimaryLinePlots(d.getProcessedArrheniusData(tempMasses),d.getCoverageLabels(tempMasses))
            # self.m_plots[3].addPrimaryLinePlots(d.getRawTempVSRawTime(), d.getCoverageLabels(tempMasses))
        # self.m_plots[0].setLegendCenterRight()
        # self.m_plots["Arrhenius Plot (Processed)"].autoScaleTopY()

        #if(showTempBounds)
        # self.m_plots["Raw Data vs. Temp."].addVerticalLine(float(self.m_tCutStartEntry.get()))
        # self.m_plots["Raw Data vs. Temp."].addVerticalLine(float(self.m_tCutEndEntry.get()))


    def checkInput(self):
        if(len(self.m_fileSelectionControl.m_filePaths) == 0): #check for file selection
            tk.messagebox.showerror("Input Files", "Please select at least one file to process.")
            return False
        if not self.m_calibOffsetEntry.InputIsValid(): return False
        if not self.m_calibScaleEntry.InputIsValid(): return False
        return True

    def prepareStartStopCutValues(self):
        t_Minima = [d.getRawTempMin() for d in self.m_parsedData]
        minStartCut = int(np.amin(t_Minima))
        if(minStartCut == 0):
            minStartCut = 1 #otherwise arrhenius plot will have 1/T -> 1/0 -> Inf value which causes bounds error
        t_Maxima = [d.getRawTempMax() for d in self.m_parsedData]
        maxStopCut = int(np.amax(t_Maxima))
        if(self.m_lowerBoundEntry.InputIsValid()):
            if(minStartCut > int(self.m_lowerBoundEntry.get())):
                self.m_lowerBoundEntry.set(str(minStartCut))
        else:
            self.m_lowerBoundEntry.set(str(minStartCut))
        if(self.m_upperBoundEntry.InputIsValid()):
            if(maxStopCut < int(self.m_upperBoundEntry.get())):
                self.m_upperBoundEntry.set(str(maxStopCut))
        else:
                self.m_upperBoundEntry.set(str(maxStopCut))

    def processInput(self):
        if(not self.checkInput()): return False
        self.m_parsedData = []
        #TODO: check input, maybe highlight missing entries!
        for f in self.m_fileSelectionControl.m_filePaths:
            wrapper = RawDataWrapper(f)
            wrapper.parseRawDataFile()
            self.m_parsedData.append(wrapper)
            self.prepareStartStopCutValues()
            wrapper.processParsedData(0,0,
                                        int(self.m_lowerBoundEntry.get()), #lower temperature boundary
                                        int(self.m_upperBoundEntry.get()), #upper temperature boundary
                                        self.m_removeBackgroundCB.instate(['selected']),
                                        self.m_smoothCountsCB.instate(['selected']),
                                        float(self.m_calibScaleEntry.get()), #calibration slope 'm' in y=mx+b
                                        float(self.m_calibOffsetEntry.get())) #calibration offset 'b' in y=mx+b

        if (self.m_normalizeCB.instate(['selected'])): #if we want to normalize data to a specific coverage
            monolayerData = None
            #find the coverage by fileName
            for w in self.m_parsedData:
                if (w.m_fileName == self.m_normSelection.get()):
                    monolayerData = w
                    break
            if( monolayerData == None):
                print("No reference coverage file selected")
                raise ValueError
            #normalize everything except the reference
            for w in [d for d in self.m_parsedData if not d == monolayerData]:
                w.normalizeDataTo(monolayerData)
            #normalize reference data last
            monolayerData.normalizeDataTo(monolayerData)


        #sort input data by coverage
        indexMapBuffer = [] #index i will contain tuple of (oldIndex,coverage) sorted by coverage
        for i in range(len(self.m_parsedData)):
            indexMapBuffer.append((i,self.m_parsedData[i].getParsedCoverageAsFloat())) #sorting input files by coverage
        indexMapBuffer.sort(reverse = False, key = lambda a : a[1])#sort, such that old index and coverage are preserved

        #buffers for different ordering
        sortedParsedDataBuffer = [] 
        sortedFilePathsBuffer = []
        for i in range(len(indexMapBuffer)):
            sortedParsedDataBuffer.append(self.m_parsedData[indexMapBuffer[i][0]])
            sortedFilePathsBuffer.append(self.m_fileSelectionControl.m_filePaths[indexMapBuffer[i][0]])
        self.m_fileSelectionControl.m_filePaths = sortedFilePathsBuffer #reference-copy
        self.m_parsedData = sortedParsedDataBuffer #reference-copy
        self.m_fileSelectionControl.prepareFileSelections()
        # self.m_fileSelectionControl.onUpdateSelection(self.m_fileSelectionControl.m_fileList)

        self.m_massDisplayOptions.resetMasses(self.m_parsedData)
        self.plotSelectedMasses()

    def saveData(self):
        if (len(self.m_parsedData) == 0):
            tk.messagebox.showerror("Save Error", "Please process some data before attempting to save it.")
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

        self.SaveProcessedDataToFile(outputFilePath,self.m_massDisplayOptions.getAllMasses(), self.m_parsedData)

    def SaveProcessedDataToFile(self, outputFilePath,massList,rawDataWrappers):
        if(massList == None or rawDataWrappers == None):
            raise ValueError
        for m in massList: #generate one .pdat file per mass (cleanest way to seperate data for masses, and keep things in an easily readable format)
            headerString = "Processed TPD data for mass " + m + \
                "\nHeader length is " + str(len(rawDataWrappers) + 4) + \
                "\nThe following files are included in this data set:\n"
            #outputData starts out column-major
            outputData = rawDataWrappers[0].m_interpolatedTemp.copy() # start with temperature column
            labels = ["Temperature"]
            coverages = [str(0.0)]
            for w in rawDataWrappers: #for each raw data file, do....
                headerString = headerString + w.m_fileName + "\n" #write filename to header for quick overview
                outputData = np.vstack((outputData, w.m_interpolatedData[m])) #append data column for mass m in outputdata
                if(w.m_parsedCoverageAvailable):
                    labels.append(w.m_parsedCoverage) #will append dosed coverage in Langmuir with "L" at the end
                else:
                    labels.append(w.m_fileName.split(" ")[0]) # this should append file number
                coverages.append(str(w.m_coverages[m]))

            headerString = headerString + "Calibration params: Temperature offset = " + str(self.m_calibOffsetEntry.get()) + " Temperature scale = " + str(self.m_calibScaleEntry.get())

            if(outputFilePath[-5:] == ".pdat"):
                outputFilePath = outputFilePath[:-5]#removing .pdat extension from user-written output file path, if it is there

            #making one file per mass, so making name based on mass number
            namedOutputFilePath = outputFilePath + ".M" + str(m) + ".pdat" #pdat for processed data
            if(path.exists(namedOutputFilePath)):
                tk.messagebox.showerror("File exists!","Please choose another name, or explicitly delete the " + outputFilePath + "to overwrite in the file explorer.")
            stringData = np.vstack((np.array(labels,dtype=str),np.array(coverages,dtype=str)))

            with open(namedOutputFilePath, mode='a') as fileHandle: #actually write file
                #write header and stringData first
                np.savetxt(fileHandle, stringData, fmt="%s", delimiter=' ', header=headerString)
                #then write float data (after transposing it)
                np.savetxt(fileHandle, outputData.transpose(), delimiter=' ')

    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        # File selection

        self.m_fileSelectionControl = InputFileListBoxControl(self.m_chordFrame, self.onUpdateFileList)
        self.m_fileSelectionControl.grid(row=0, column=0, columnspan=4, sticky = "nsew")


        # Processing options:

        self.m_optionsLabel = ttk.Label(self.m_chordFrame, text="Processing Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chordFrame, text="Lower Boundary (Temp.):")
        self.m_tCutStartLabel.grid(row=4, column = 1, sticky = "nse")

        self.m_lowerBoundEntry = EnhancedEntry(self.m_chordFrame, inputValueType = int,
            errorTitle = "Lower Boundary (Temp.)", errorMessage = "Please enter an integer for the lower temperature boundary")
        self.m_lowerBoundEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chordFrame, text="Upper Boundary (Temp.):")
        self.m_tCutEndLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_upperBoundEntry = EnhancedEntry(self.m_chordFrame, inputValueType = int,
            errorTitle = "Upper Boundary (Temp.)", errorMessage = "Please enter an integer for the upper temperature boundary.")
        self.m_upperBoundEntry.grid(row=5, column = 2, sticky = "nsw")

        #Temperature (thermocouple) calibration options:

        self.m_calibLabel = ttk.Label(self.m_chordFrame, text="Temperature Calibration:")#, compound = tk.CENTER)
        self.m_calibLabel.grid(row=6, column = 0, columnspan = 2, sticky = "nsw")

        self.m_calibFormulaLabel = ttk.Label(self.m_chordFrame, text="( T_Calibrated = Scale * T_RawData + Offset )")
        self.m_calibFormulaLabel.grid(row=7, column = 0, columnspan = 3)#, sticky = "nse")

        self.m_calibOffsetLabel = ttk.Label(self.m_chordFrame, text="Offset:")
        self.m_calibOffsetLabel.grid(row=8 , column = 1, sticky = "nse")

        self.m_calibOffsetEntry = EnhancedEntry(self.m_chordFrame, inputValueType = float,
            errorTitle = "Calibration Offset", errorMessage= "Please enter a decimal for the temperature calibration offset.")
        self.m_calibOffsetEntry.grid(row=8 , column = 2, sticky = "nsw")
        self.m_calibOffsetEntry.setBackingVar("0.836")#default

        self.m_calibScaleLabel = ttk.Label(self.m_chordFrame, text="Scale:")
        self.m_calibScaleLabel.grid(row=9, column = 1, sticky = "nse")

        self.m_calibScaleEntry = EnhancedEntry(self.m_chordFrame, inputValueType = float,
            errorTitle = "Calibration Scale", errorMessage = "Please enter a decimal for the temperature calibration scale.")
        self.m_calibScaleEntry.grid(row=9, column = 2, sticky = "nsw")
        self.m_calibScaleEntry.setBackingVar("0.985")#default


        # Checkbuttons + Comboboxes for options:

        self.m_smoothTempCB = EnhancedCheckButton(self.m_chordFrame, text="Smooth Temperature")
        self.m_smoothTempCB.grid(row = 10, column = 1, sticky = "nsw")
        self.m_smoothTempCB.set(1)
        self.m_smoothTempCB.configure(state = tk.DISABLED)

        self.m_smoothCountsCB = EnhancedCheckButton(self.m_chordFrame, text="Smooth Counts/s")
        self.m_smoothCountsCB.grid(row = 10, column = 2, sticky = "nsw")

        self.m_normalizeCB = EnhancedCheckButton(self.m_chordFrame, text = "Normalize to coverage of (select file):", command=self.toggleNormalizeCB)
        self.m_normalizeCB.grid(row = 11, column = 1, sticky = "nsw")

        self.m_removeBackgroundCB = EnhancedCheckButton(self.m_chordFrame, text="Remove Background")
        self.m_removeBackgroundCB.grid(row = 11, column = 2, sticky = "nsw")

        self.m_normSelection = ttk.Combobox(self.m_chordFrame, state = tk.DISABLED)
        self.m_normSelection.grid(row=12, column=1, columnspan=2, sticky= "nsew")

        self.m_subtractCB = EnhancedCheckButton(self.m_chordFrame, text = "Subtract Spectrum (select file):", command=self.toggleSubtractCB, state = tk.DISABLED)
        self.m_subtractCB.grid(row = 13, column = 1, sticky = "nsw")

        self.m_subtractSelection = ttk.Combobox(self.m_chordFrame, state = tk.DISABLED)
        self.m_subtractSelection.grid(row=14, column=1, columnspan=2, sticky= "nsew")

        #Process Button

        self.m_processButton = ttk.Button(self.m_chordFrame, text = "Process Input", command = self.processInput)
        self.m_processButton.grid(row=15, column = 1, columnspan=2, sticky = "nsew")

        #Display options

        self.m_displayOptionsLabel = ttk.Label(self.m_chordFrame, text='Display Options:')
        self.m_displayOptionsLabel.grid(row = 16, column = 0, columnspan = 2, sticky="nsw")

        self.m_toggleMarkersButton = ttk.Button(self.m_chordFrame, text = "Toggle Markers", command = self.toggleMarkers)
        self.m_toggleMarkersButton.grid(row=17, column = 1, columnspan=2, sticky = "nsew")

        self.m_massDisplayOptions = DisplayOptionsFrame(self.m_chordFrame, self.plotSelectedMasses)
        self.m_massDisplayOptions.grid(row = 18, column = 0, columnspan = 4, sticky = "nsew")

        # self.m_massDisplayOptions.m_availableMassesListBox

        self.m_saveDataButton = ttk.Button(self.m_chordFrame, text = "Save Processed Data", command = self.saveData)
        self.m_saveDataButton.grid(row=19, column = 1, columnspan=3, sticky = "nsew")

        # for child in self.m_chordFrame.winfo_children():
        #     child.grid_configure(padx=3, pady=3)

        # for child in self.m_fileButtonFrame.winfo_children():
        #     child.pack_configure(padx=3, pady=3)

        # for child in self.m_massDisplayOptions.winfo_children():
        #     child.grid_configure(padx=3, pady=3)

        self.m_chordFrame.grid_columnconfigure(index=0, weight=1)
        self.m_chordFrame.grid_columnconfigure(index=1, weight=1)
        self.m_chordFrame.grid_columnconfigure(index=2, weight=1)
        self.m_chordFrame.grid_columnconfigure(index=3, weight=1)
