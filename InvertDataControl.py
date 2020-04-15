import tkinter as tk
import tkinter.ttk as ttk
from PlotsFrame import MPLContainer
from Controls import Chord, ScrolledListBox, EnhancedCheckButton, ProcessingStepControlBase #ui element
from tkinter.filedialog import askdirectory, askopenfilenames

class InvertDataControl(ProcessingStepControlBase):
    def __init__(self):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)")

    def selectFiles(self):
        #from OS API
        raise NotImplementedError

    def deselectFiles(self):
        #remove some selected files
        raise NotImplementedError

    def useProcessedFiles(self):
        #grab processed data from processRawDataControl
        raise NotImplementedError

    def processInput(self):
        self.m_parsedData = []
        #go for inversion here
        raise NotImplementedError

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "First graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Second graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Third graph", bg="white"))

        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)

        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_parent = parent
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)

        # File selection

        self.m_filesListBoxLabel = ttk.Label(self.m_chord, text='Input files:')
        self.m_filesListBoxLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_filesListBox = ScrolledListBox(self.m_chord)
        self.m_filesListBox.grid(row = 1, column = 0, columnspan = 4, sticky = "nsew")

        self.m_fileButtonFrame = ttk.Frame(self.m_chord)
        self.m_fileButtonFrame.grid(row=2, column = 0, columnspan = 3, sticky = "nsew")

        self.m_selectButton = ttk.Button(self.m_fileButtonFrame,text="Select Files",command = self.selectFiles)
        self.m_selectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove Selected",command = self.deselectFiles)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_useProcessedButton = ttk.Button(self.m_fileButtonFrame,text="Remove Selected",command = self.useProcessedFiles)
        self.m_useProcessedButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        for child in self.m_chord.winfo_children():
            child.grid_configure(padx=3, pady=3)

        for child in self.m_fileButtonFrame.winfo_children():
            child.pack_configure(padx=3, pady=3)

        self.m_chord.grid_columnconfigure(index=0, weight=1)
        self.m_chord.grid_columnconfigure(index=1, weight=1)
        self.m_chord.grid_columnconfigure(index=2, weight=1)