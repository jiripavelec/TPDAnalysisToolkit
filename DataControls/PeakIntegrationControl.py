import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer # pylint: disable=import-error
from DataControls.ControlElements import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingControlBase, EnhancedEntry, DisplayOptionsFrame, SingleInputFileSelectionControl #ui element # pylint: disable=import-error
from DataModels.ProcessedDataWrapper import ProcessedDataWrapper # pylint: disable=import-error
from tkinter.filedialog import askopenfilename

#This class allows for integration of a peak (processed data) in between
#two selected boundaries.
#Uses the processed data wrapper as an interface.
class PeakIntegrationControl(ProcessingControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Peak Integration", controller, accordion)
        self.m_parsedData = None
        self.m_plots["Processed Data"] = MPLContainer(self.m_chord.m_notebookRef, "Processed Data", "Desorption Rate (arb. U.)", "Temperature (K)", root)
        self.m_integrated = False

    def onFileSelected(self):
        self.m_parsedData = ProcessedDataWrapper(self.m_fileSelectionControl.m_inputFilePath)
        self.m_parsedData.parseProcessedDataFile()
        self.m_spectrumCB["values"] = self.m_parsedData.m_includedFiles
        # self.m_spectrumCB.current(0)

    def plotBounds(self):
        self.m_plots["Processed Data"].removeVerticalLines()
        # if(not self.m_integrated):
        self.m_plots["Processed Data"].addVerticalLine(float(self.m_upperBoundEntry.get()))
        self.m_plots["Processed Data"].addVerticalLine(float(self.m_lowerBoundEntry.get()))

    def plotSelectedSpectrum(self):
        targetData = self.m_parsedData.fileNameToExpDesorptionRateVSTemp(self.m_spectrumCB.get())
        targetLabel = self.m_parsedData.fileNameToCoverageLabel(self.m_spectrumCB.get())
        self.m_plots["Processed Data"].clearPlots()
        self.m_plots["Processed Data"].addPrimaryLinePlots(targetData,targetLabel, color = 'b')
        self.plotBounds()
        # if(self.m_integrated): #shade, currently has performance problems when drawing polygon
        #     t2 = float(self.m_tCutEndEntry.get())
        #     t1 = float(self.m_tCutStartEntry.get())
        #     curve = self.m_parsedData.getProcessedDataBetweenForFile(t1,t2,self.m_spectrumCB.get())
        #     self.m_plots["Processed Data"].shadeBelowCurve(curve[0],curve[1])
        

    def onSpectrumSelected(self, *args, **kwargs):
        if(self.m_parsedData != None):
            self.m_integrated = False
            self.checkIntegrationBounds()
            self.plotSelectedSpectrum()

    def checkIntegrationBounds(self):
        minStartCut = int(self.m_parsedData.getMinTemp())
        maxStopCut = int(self.m_parsedData.getMaxTemp())
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

    def onBoundsChanged(self):
        self.checkIntegrationBounds()

    def processInput(self):
        self.checkIntegrationBounds()
        t2 = float(self.m_upperBoundEntry.get())
        t1 = float(self.m_lowerBoundEntry.get())
        result = self.m_parsedData.integrateDesorptionRate(t1,t2,self.m_spectrumCB.get())
        self.m_integrated = True
        self.m_resultValueLabel.configure(text = str(result))
        self.plotSelectedSpectrum()#should update plot with appropriate shading

    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        # File selection

        self.m_fileSelectionControl = SingleInputFileSelectionControl(self.m_chordFrame, onSelect=self.onFileSelected)
        self.m_fileSelectionControl.grid(row=0, column = 0, columnspan = 4, sticky = "nsew")

        # Spectrum selection

        self.m_spectrumSelectionLabel = ttk.Label(self.m_chordFrame, text='Select TPD Spectrum for Integration:')
        self.m_spectrumSelectionLabel.grid(row = 1, column = 0, columnspan = 2, sticky="nsw")

        self.m_spectrumCB = ttk.Combobox(self.m_chordFrame)
        self.m_spectrumCB.configure(state = 'readonly')
        self.m_spectrumCB.bind("<<ComboboxSelected>>", self.onSpectrumSelected) #binding to event because CB does not have 'command' param
        self.m_spectrumCB.grid(row = 2, column = 0, columnspan = 3, sticky = "nsew")
        
        # self.m_spectrumSelectionLabel = ttk.Label(self.m_chordFrame, text='Select Mass Spectrum for Integration:')
        # self.m_spectrumSelectionLabel.grid(row = 3, column = 0, columnspan = 2, sticky="nsw")

        # self.m_spectrumCB = ttk.Combobox(self.m_chordFrame)
        # # self.m_prefactorCB.bind("<<ComboboxSelected>>", self.plotDataForSelectedPrefactor) #binding to event because CB does not have 'command' param
        # self.m_spectrumCB.grid(row = 4, column = 0, columnspan = 3, sticky = "nsew")

        # Integration Options

        self.m_optionsLabel = ttk.Label(self.m_chordFrame, text="Integration Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=5, column = 0, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chordFrame, text="Initial Temperature:")
        self.m_tCutStartLabel.grid(row=6, column = 1, sticky = "nse")

        self.m_lowerBoundEntry = EnhancedEntry(self.m_chordFrame, inputValueType = int,
            errorTitle= "Initial Temperature", errorMessage="Please enter an integer for the temperature at which to start integration.")
        self.m_lowerBoundEntry.grid(row=6, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chordFrame, text="Final Temperature:")
        self.m_tCutEndLabel.grid(row=7, column = 1, sticky = "nse")

        self.m_upperBoundEntry = EnhancedEntry(self.m_chordFrame, inputValueType= int,
            errorTitle="Final Temperature", errorMessage="Please enter an integer for the temperature at which to end integration.")
        self.m_upperBoundEntry.grid(row=7, column = 2, sticky = "nsw")

        self.m_resultTitleLabel = ttk.Label(self.m_chordFrame, text="Integration Result:")
        self.m_resultTitleLabel.grid(row=8, column = 1, sticky = "nse")

        self.m_resultValueLabel = ttk.Label(self.m_chordFrame, text="N/A")
        self.m_resultValueLabel.grid(row=8, column = 2, sticky = "nsw")

        # Display Options

        # self.m_showBoundsCB = EnhancedCheckButton(self.m_chordFrame, text="Show Temp. Bounds")

        #Process Button

        self.m_processButton = ttk.Button(self.m_chordFrame, text = "Integrate", command = self.processInput)
        self.m_processButton.grid(row=9, column = 0, columnspan=4, sticky = "nsew")



