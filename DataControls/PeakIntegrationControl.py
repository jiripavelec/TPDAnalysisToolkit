import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer # pylint: disable=import-error
from DataControls.ControlElements import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase, EnhancedEntry, DisplayOptionsFrame, SingleInputFileSelectionControl #ui element # pylint: disable=import-error
from tkinter.filedialog import askopenfilename

class PeakIntegrationControl(ProcessingStepControlBase):
    def __init__(self, controller, root, accordion):
        super().__init__("Peak Integration (WIP)", controller, accordion)
        self.m_parsedData = None
        self.m_plots["Processed Data"] = MPLContainer(self.m_chord.m_notebookRef, "Processed Data", "Desorption Rate (arb. U.)", "Temperature (K)", root)

    def initChordUI(self):
        self.m_chordFrame = self.m_chord.m_scrollable_frame

        # File selection

        self.m_fileSelectionControl = SingleInputFileSelectionControl(self.m_chordFrame)
        self.m_fileSelectionControl.grid(row=0, column = 0, columnspan = 4, sticky = "nsew")

        # Integration Options

        self.m_optionsLabel = ttk.Label(self.m_chordFrame, text="Integration Options:")#, compound = tk.CENTER)
        self.m_optionsLabel.grid(row=1, column = 0, sticky = "nsw")
        
        self.m_tCutStartLabel = ttk.Label(self.m_chordFrame, text="Initial Temperature:")
        self.m_tCutStartLabel.grid(row=4, column = 1, sticky = "nse")

        self.m_tCutStartEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tCutStartEntry.grid(row=4, column = 2, sticky = "nsw")

        self.m_tCutEndLabel = ttk.Label(self.m_chordFrame, text="Final Temperature:")
        self.m_tCutEndLabel.grid(row=5, column = 1, sticky = "nse")

        self.m_tCutEndEntry = EnhancedEntry(self.m_chordFrame)
        self.m_tCutEndEntry.grid(row=5, column = 2, sticky = "nsw")

