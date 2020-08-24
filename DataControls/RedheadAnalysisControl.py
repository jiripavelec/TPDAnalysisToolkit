import tkinter as tk
import tkinter.ttk as ttk
from DataControls.ControlElements import Chord, ProcessingStepControlBase #ui element # pylint: disable=import-error

class RedheadAnalysisControl(ProcessingStepControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Redhead Analysis (WIP)", controller, accordion)

    def initNotebook(self,  root):
        pass
    
    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        self.m_Label = ttk.Label(self.m_chordFrame, text='Work in Progress')
        self.m_Label.grid(row = 0, column = 0, columnspan = 4, sticky="nsew")