import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, DisplayOptionsFrame, EnhancedEntry #ui element
from tkinter.filedialog import askdirectory, askopenfilenames, asksaveasfilename
from RawDataWrapper import RawDataWrapper
import numpy as np


class ProcessRawDataControl(ProcessingStepControlBase):
    def __init__(self, controller):
        super().__init__("Process TPD Data", controller)
        # self.m_filesDirectory = ""

    def selectFiles(self):
        # self.m_filesDirectory = askdirectory()
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
            self.m_subtractSelection["values"] = self.m_fileList
            self.m_normSelection["values"] = self.m_fileList

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
        self.m_normSelection["values"] = self.m_fileList

        # for i in range(len(self.m_filePaths)):
        #     print(self.m_filePaths[i] + " " + self.m_filesListBox.get(i))

    def toggleSubtractCB(self):
        if(self.m_subtractCB.instate(['!selected'])):
            self.m_subtractSelection.configure(state = tk.DISABLED)
        else:
            self.m_subtractSelection.configure(state = tk.NORMAL)

    def toggleNormalizeCB(self):
        if(self.m_normalizeCB.instate(['!selected'])):
            self.m_normSelection.configure(state = tk.DISABLED)
        else:
            self.m_normSelection.configure(state = tk.NORMAL)

    def plotSelectedMasses(self):
        for c in self.mplContainers:
            c.clearPlots()

        for d in self.m_parsedData:
            self.mplContainers[0].addLinePlots(d.getRawData(self.m_massDisplayOptions.getMassesToDisplay()))
            self.mplContainers[1].addLinePlots(d.getProcessedData(self.m_massDisplayOptions.getMassesToDisplay()))

    def processInput(self):
        self.m_parsedData = []
        #TODO: check input, maybe highlight missing entries!
        for f in self.m_filePaths:
            wrapper = RawDataWrapper(f)
            wrapper.parseRawDataFile()
            self.m_parsedData.append(wrapper)
            wrapper.processParsedData(int(self.m_tRampStartEntry.get()),
                                        int(self.m_tRampEndEntry.get()),
                                        int(self.m_tCutStartEntry.get()),
                                        int(self.m_tCutEndEntry.get()),
                                        self.m_removeBackgroundCB.instate(['selected']),
                                        self.m_smoothCB.instate(['selected']))

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

        self.m_massDisplayOptions.resetMasses(self.m_parsedData)
        self.plotSelectedMasses()

        #TODO: autosave result

    def saveData(self):
        if (len(self.m_parsedData) == 0):
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
        dateTimeString = str(datetime.now()).replace('-','').replace(' ', '_').replace(':','')
        fileName = fileName + '.' + dateTimeString

        for m in self.m_massDisplayOptions.getAllMasses():
            headerString = "Processed TPD data for mass " + m + "\nThe following files are included in this data set:\n"
            #outputData starts out column-major
            outputData = self.m_parsedData[0].m_interpolatedTemp.copy() # start with temperature column
            labels = ["Temperature"]
            coverages = [str(0.0)]
            for w in self.m_parsedData:
                headerString = headerString + w.m_fileName + "\n" #write filename to header for quick overview
                outputData = np.vstack((outputData, w.m_interpolatedData[m])) #append data column for mass m in outputdata
                labels.append(w.m_fileName.split(" ")[0]) # this should append file number
                coverages.append(str(w.m_coverages[m]))
            
            #make one file per mass
            namedOutputFilePath = outputFilePath + '/' + fileName + ".Mass_" + str(m) + ".pdat" #pdat for processed data
            stringData = np.vstack((np.array(labels,dtype=str),np.array(coverages,dtype=str)))

            with open(namedOutputFilePath, mode='a') as fileHandle:
                #write header and stringData first
                np.savetxt(fileHandle, stringData, fmt="%s", delimiter=' ', header=headerString)
                #then write float data (after transposing it)
                np.savetxt(fileHandle, outputData.transpose(), delimiter=' ')



    # def getProcessedData(self):
    #     return self.m_parsedData

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)
        self.mplContainers.append(MPLContainer(self.m_notebook, "Raw Data", "Desorption Rate", "Temperature (K)"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Processed Data", "Desorption Rate", "Temperature (K)"))

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

        self.m_fileButtonFrame = ttk.Frame(self.m_chord)
        self.m_fileButtonFrame.grid(row=2, column = 0, columnspan = 3, sticky = "nsew")

        self.m_selectButton = ttk.Button(self.m_fileButtonFrame,text="Select Files",command = self.selectFiles)
        self.m_selectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove Selected",command = self.deselectFiles)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        # Options

        self.m_optionsLabel = ttk.Label(self.m_chord, text="Processing Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chord, text="Cut Data Start Temp.:")
        self.m_tCutStartLabel.grid(row=4, column = 1, sticky = "nse")

        self.m_tCutStartEntry = EnhancedEntry(self.m_chord)
        self.m_tCutStartEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chord, text="Cut Data End Temp.:")
        self.m_tCutEndLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tCutEndEntry = EnhancedEntry(self.m_chord)
        self.m_tCutEndEntry.grid(row=5, column = 2, sticky = "nsw")

        self.m_tRampStartLabel = ttk.Label(self.m_chord, text="Ramp Start Temp.:")
        self.m_tRampStartLabel.grid(row=6, column = 1, sticky = "nse")

        self.m_tRampStartEntry = EnhancedEntry(self.m_chord)
        self.m_tRampStartEntry.grid(row=6, column = 2, sticky = "nsw")

        self.m_tRampEndLabel = ttk.Label(self.m_chord, text="Ramp End Temp.:")
        self.m_tRampEndLabel.grid(row=7, column = 1, sticky = "nse")

        self.m_tRampEndEntry = EnhancedEntry(self.m_chord)
        self.m_tRampEndEntry.grid(row=7, column = 2, sticky = "nsw")

        # Checkbuttons + Comboboxes for options:

        self.m_smoothCB = EnhancedCheckButton(self.m_chord, text="Smooth")
        self.m_smoothCB.grid(row = 8, column = 1, sticky = "nsw")

        self.m_removeBackgroundCB = EnhancedCheckButton(self.m_chord, text="Remove Background")
        self.m_removeBackgroundCB.grid(row = 8, column = 2, sticky = "nsw")

        self.m_normalizeCB = EnhancedCheckButton(self.m_chord, text = "Normalize", command=self.toggleNormalizeCB)
        self.m_normalizeCB.grid(row = 9, column = 1, sticky = "nsw")

        self.m_normSelection = ttk.Combobox(self.m_chord, state = tk.DISABLED)
        self.m_normSelection.grid(row=10, column=1, columnspan=2, sticky= "nsew")

        self.m_subtractCB = EnhancedCheckButton(self.m_chord, text = "Subtract Spectrum", command=self.toggleSubtractCB, state = tk.DISABLED)
        self.m_subtractCB.grid(row = 11, column = 1, sticky = "nsw")

        self.m_subtractSelection = ttk.Combobox(self.m_chord, state = tk.DISABLED)
        self.m_subtractSelection.grid(row=12, column=1, columnspan=2, sticky= "nsew")

        #Process Button

        self.m_processButton = ttk.Button(self.m_chord, text = "Process Input", command = self.processInput)
        self.m_processButton.grid(row=13, column = 1, columnspan=2, sticky = "nse")

        #Display options

        self.m_displayOptionsLabel = ttk.Label(self.m_chord, text='Display Options')
        self.m_displayOptionsLabel.grid(row = 14, column = 0, columnspan = 2, sticky="nsw")

        self.m_massDisplayOptions = DisplayOptionsFrame(self.m_chord, self.plotSelectedMasses)
        self.m_massDisplayOptions.grid(row = 15, column = 1, columnspan = 2, sticky = "nsw")

        self.m_massDisplayOptions.m_availableMassesListBox

        self.m_saveDataButton = ttk.Button(self.m_chord, text = "Save Processed Data for Selected Masses", command = self.saveData)
        self.m_saveDataButton.grid(row=16, column = 0, columnspan=3, sticky = "nsew")

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
