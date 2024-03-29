import tkinter as tk
import tkinter.ttk as ttk
from DataControls.ControlElements import Chord, ProcessingControlBase, InputFileListBoxControl, EnhancedEntry # pylint: disable=import-error
from PlotsFrame import MPLContainer # pylint: disable=import-error

#This is WORK-IN-PROGRESS meaning its an unfinished class.
#It is intended to provide more accurate coverage calibration on basis
#of nominal dose (set in LabVIEW software, assumed to be true)
#versus integrated number of counts
class CoverageCalibrationControl(ProcessingControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Coverage Calibration (WIP)", controller, accordion)
        self.m_plots["Coverage"] = MPLContainer(self.m_chord.m_notebookRef, "Coverage", "Desorption Rate", "Temperature (K)", root)
        self.m_forwardXFactor = 1.0
        self.m_inverseXFactor = 1.0
        self.m_forwardYFactor = 1.0
        self.m_inverseYFactor = 1.0
        self.m_plots["Coverage"].addSecondaryScaledXAxis(self.forwardXTransform,self.inverseXTransform)
        self.m_plots["Coverage"].addSecondaryScaledYAxis(self.forwardYTransform,self.inverseYTransform)

    def forwardXTransform(self, x):
        return x*self.m_forwardXFactor

    def inverseXTransform(self, x):
        return x*self.m_inverseXFactor

    def forwardYTransform(self, y):
        return y*self.m_forwardYFactor

    def inverseYTransform(self, y):
        return y*self.m_inverseYFactor

    def adaptTransformTest(self):
        self.m_forwardXFactor = 2.0
        self.m_inverseXFactor = 0.5

    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame


        self.m_fileSelectionControl = InputFileListBoxControl(self.m_chordFrame, lambda e : None)
        self.m_fileSelectionControl.grid(row = 0, column = 0, columnspan = 4, sticky="nsew")

        self.m_optionsLabel = ttk.Label(self.m_chordFrame, text="Processing Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=3, column = 0, columnspan = 2, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chordFrame, text="Cut Data Start Temp.:")
        self.m_tCutStartLabel.grid(row=4, column = 1, sticky = "nse")

        self.m_tCutStartEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tCutStartEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chordFrame, text="Cut Data End Temp.:")
        self.m_tCutEndLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tCutEndEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tCutEndEntry.grid(row=5, column = 2, sticky = "nsw")

        self.m_testButton = ttk.Button(self.m_chordFrame,text="test",command = self.adaptTransformTest)
        self.m_testButton.grid(row = 6, column = 0, columnspan = 4, sticky="nsew")

        self.m_Label = ttk.Label(self.m_chordFrame, text='Work in Progress')
        self.m_Label.grid(row = 7, column = 0, columnspan = 4, sticky="nsew")

        self.m_chordFrame.grid_columnconfigure(index=0, weight=1, uniform= "test1")
        self.m_chordFrame.grid_columnconfigure(index=1, weight=1, uniform= "test1")
        self.m_chordFrame.grid_columnconfigure(index=2, weight=1, uniform= "test2")
        self.m_chordFrame.grid_columnconfigure(index=3, weight=1, uniform= "test3")

