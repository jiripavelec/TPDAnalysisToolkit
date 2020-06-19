import tkinter as tk
import tkinter.ttk as ttk
from DataControls.ControlElements import Chord, ProcessingStepControlBase # pylint: disable=import-error
from PlotsFrame import MPLContainer # pylint: disable=import-error

class CoverageCalibrationControl(ProcessingStepControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Coverage Calibration", controller, accordion)
        self.m_plots["Coverage"] = MPLContainer(self.m_chord.m_notebookRef, "Coverage", "Desorption Rate", "Temperature (K)", root)



    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        self.m_Label = ttk.Label(self.m_chordFrame, text='Work in Progress')
        self.m_Label.grid(row = 0, column = 0, columnspan = 4, sticky="nsew")