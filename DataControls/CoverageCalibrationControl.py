import tkinter as tk
import tkinter.ttk as ttk
from DataControls.ControlElements import Chord, ProcessingStepControlBase # pylint: disable=import-error
from PlotsFrame import MPLContainer # pylint: disable=import-error

class CoverageCalibrationControl(ProcessingStepControlBase):
    def __init__(self, controller, root):
        super().__init__("Coverage Calibration", controller)

    def initNotebook(self, parent, root):
        self.m_notebook = ttk.Notebook(parent)
        self.mplContainers.append(MPLContainer(self.m_notebook, "Coverage", "Desorption Rate", "Temperature (K)", root))
        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)
        self.m_notebook.grid(row=0,column=0,sticky="nsew")


    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        self.m_Label = ttk.Label(self.m_chordFrame, text='Work in Progress')
        self.m_Label.grid(row = 0, column = 0, columnspan = 4, sticky="nsew")