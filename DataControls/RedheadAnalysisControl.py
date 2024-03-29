import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer # pylint: disable=import-error
from DataControls.ControlElements import Chord, ProcessingControlBase, EnhancedEntry, SingleInputFileSelectionControl #ui element # pylint: disable=import-error
from DataModels.ProcessedDataWrapper import ProcessedDataWrapper # pylint: disable=import-error
import numpy as np

#This is WORK-IN-PROGRESS meaning its an unfinished class.
#It is intended to allow for redhead analysis of processed data.
class RedheadAnalysisControl(ProcessingControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Redhead Analysis (WIP)", controller, accordion)
        self.m_parsedData = None
        self.m_plots["Processed Data"] = MPLContainer(self.m_chord.m_notebookRef, "Processed Data", "Desorption Rate (arb. U.)", "Temperature (K)", root)
        self.m_plots["Arrhenius Plot (Processed)"] = MPLContainer(self.m_chord.m_notebookRef, "Arrhenius Plot (Processed)", "ln(Desorption Rate)", "Reciprocal Temperature (1/K)", root, invertXAxis=True)
    
    def onFileSelected(self):
        self.m_parsedData = ProcessedDataWrapper(self.m_fileSelectionControl.m_inputFilePath)
        self.m_parsedData.parseProcessedDataFile()
        if(self.m_parsedData.m_normalized):
            tk.messagebox.showerror("Input Data", "Please use processed data which has not been normalized to a monolayer!")
            self.m_spectrumCB["values"] = None
        else:    
            self.m_spectrumCB["values"] = self.m_parsedData.m_includedFiles
        # self.m_spectrumCB.current(0)

    def plotBounds(self):
        # for plot in self.m_plots.values():
        #     plot.removeVerticalLines()
        #     plot.addVerticalLine(float(self.m_tCutEndEntry.get()))
        #     plot.addVerticalLine(float(self.m_tCutStartEntry.get()))

        self.m_plots["Processed Data"].removeVerticalLines()
        # if(not self.m_integrated):
        self.m_plots["Processed Data"].addVerticalLine(float(self.m_tCutEndEntry.get()))
        self.m_plots["Processed Data"].addVerticalLine(float(self.m_tCutStartEntry.get()))

    def plotSelectedSpectrum(self):
        targetData = self.m_parsedData.fileNameToExpDesorptionRateVSTemp(self.m_spectrumCB.get())
        targetLabel = self.m_parsedData.fileNameToCoverageLabel(self.m_spectrumCB.get())

        arrheniusData = np.vstack((np.reciprocal(targetData[0,:]),np.log(targetData[1,:])))

        self.m_plots["Processed Data"].clearPlots()
        self.m_plots["Processed Data"].addPrimaryLinePlots(targetData,targetLabel, color = 'b')

        self.m_plots["Arrhenius Plot (Processed)"].clearPlots()
        self.m_plots["Arrhenius Plot (Processed)"].addPrimaryLinePlots(arrheniusData,targetLabel, color = 'b')

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

    def tryReadStartCutEntry(self):
        if(self.m_tCutStartEntry.get() == ''):
            return False
        try:
            int(self.m_tCutStartEntry.get())
        except ValueError:
            tk.messagebox.showerror("Initial Temperature", "Please enter an integer for the temperature at which to start integration.")
            return False
        return True

    def tryReadStopCutEntry(self):
        if(self.m_tCutEndEntry.get() == ''):
            return False
        try:
            int(self.m_tCutEndEntry.get())
        except ValueError:
            tk.messagebox.showerror("Final Temperature", "Please enter an integer for the temperature at which to end integration.")
            return False
        return True

    def checkIntegrationBounds(self):
        minStartCut = int(self.m_parsedData.getMinTemp())
        maxStopCut = int(self.m_parsedData.getMaxTemp())
        if(self.tryReadStartCutEntry()):
            if(minStartCut > int(self.m_tCutStartEntry.get())):
                self.m_tCutStartEntry.set(str(minStartCut))
        else:
            self.m_tCutStartEntry.set(str(minStartCut))
        if(self.tryReadStopCutEntry()):
            if(maxStopCut < int(self.m_tCutEndEntry.get())):
                self.m_tCutEndEntry.set(str(maxStopCut))
        else:
                self.m_tCutEndEntry.set(str(maxStopCut))

    def onBoundsChanged(self):
        self.checkIntegrationBounds()

    def processInput(self):
        self.checkIntegrationBounds()
        t2 = float(self.m_tCutEndEntry.get())
        t1 = float(self.m_tCutStartEntry.get())
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

        self.m_optionsLabel = ttk.Label(self.m_chordFrame, text="Fitting Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=5, column = 0, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chordFrame, text="Lower Boundary")
        self.m_tCutStartLabel.grid(row=6, column = 1, sticky = "nse")

        self.m_tCutStartEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tCutStartEntry.grid(row=6, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chordFrame, text="Upper Boundary")
        self.m_tCutEndLabel.grid(row=7, column = 1, sticky = "nse")

        self.m_tCutEndEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tCutEndEntry.grid(row=7, column = 2, sticky = "nsw")

        self.m_resultTitleLabel = ttk.Label(self.m_chordFrame, text="Fitting Results:")
        self.m_resultTitleLabel.grid(row=8, column = 1, sticky = "nse")

        self.m_resultValueLabel = ttk.Label(self.m_chordFrame, text="N/A")
        self.m_resultValueLabel.grid(row=8, column = 2, sticky = "nsw")

        self.m_Label = ttk.Label(self.m_chordFrame, text='Work in Progress')
        self.m_Label.grid(row = 9, column = 0, columnspan = 4, sticky="nsew")