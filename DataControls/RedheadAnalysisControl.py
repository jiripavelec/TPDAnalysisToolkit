import tkinter as tk
import tkinter.ttk as ttk
from DataControls.ControlElements import Chord, ProcessingStepControlBase #ui element # pylint: disable=import-error

class RedheadAnalysisControl(ProcessingStepControlBase):
    def __init__(self, controller, root):
        super().__init__("Redhead Analysis (To Be Done)", controller)

    def initNotebook(self, parent, root):
        self.m_notebook = ttk.Notebook(parent)

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        self.m_Label = ttk.Label(self.m_chordFrame, text='Work in Progress')
        self.m_Label.grid(row = 0, column = 0, columnspan = 4, sticky="nsew")