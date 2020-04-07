import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from tkinter.filedialog import askdirectory, askopenfilenames

class InvertDataControl(ProcessingStepControlBase):
    def __init__(self):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)")

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "First graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Second graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Third graph", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)
        tk.Label(self.m_chord, text='hello world, I am different!', bg='white').pack()