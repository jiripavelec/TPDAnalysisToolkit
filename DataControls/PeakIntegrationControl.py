import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer # pylint: disable=import-error
from DataControls.ControlElements import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, EnhancedEntry, DisplayOptionsFrame, SingleInputFileSelectionControl #ui element # pylint: disable=import-error
from tkinter.filedialog import askopenfilename

class PeakIntegrationControl(ProcessingStepControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Peak Integration (WIP)", controller, accordion)

    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        # File selection
        
        self.m_fileSelectionControl = SingleInputFileSelectionControl(self.m_chordFrame)
        self.m_fileSelectionControl.grid(row=0, column = 0, columnspan = 4, sticky = "nsew")