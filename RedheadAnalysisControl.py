import tkinter as tk
import tkinter.ttk as ttk
from Controls import Chord, ProcessingStepControlBase #ui element

class RedheadAnalysisControl(ProcessingStepControlBase):
    def __init__(self, controller):
        super().__init__("Redhead Analysis (To Be Done)", controller)

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)

        self.m_Label = ttk.Label(self.m_chord, text='Work in Progress')
        self.m_Label.grid(row = 0, column = 0, columnspan = 4, sticky="nsew")