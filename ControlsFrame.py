import tkinter as tk
import tkinter.ttk as ttk
from Controls import Accordion
from ProcessRawDataControl import ProcessRawDataControl
from InvertDataControl import InvertDataControl
from RedheadAnalysisControl import RedheadAnalysisControl

#ControlsFrame BEGIN
class ControlsFrame(tk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        self.Controls = []
        self.initUI(parent, root)

    def initUI(self, parent, root):
        self.accordion = Accordion(self)
        
        #For raw data processing
        self.m_rawDataControl = ProcessRawDataControl(self, root)
        self.Controls.append(self.m_rawDataControl)

        #For inversion of processed data
        self.m_invertDataControl = InvertDataControl(self, root)
        self.Controls.append(self.m_invertDataControl)

        #For redhead analysis
        self.m_redheadAnalysisControl = RedheadAnalysisControl(self, root)
        self.Controls.append(self.m_redheadAnalysisControl)

        #separator for easier displaying
        self.m_separator = ttk.Separator(self)
        self.m_separator.pack(side = tk.RIGHT, fill= tk.Y)

    def initChords(self,plotsFrame, root):
        for c in self.Controls:
            c.initNotebook(plotsFrame, root)
            c.initChordUI(self.accordion)
        self.accordion.append_chords([c.m_chordContainer for c in self.Controls])
        self.accordion.pack(side = tk.LEFT, fill=tk.BOTH, expand = True)

    # def requestProcessedData(self):
    #     return self.m_rawDataControl.getProcessedData()

    # def registerControl(self, control):
    #     # self.Controls[control.m_title] = control
    #     self.Controls.append(control)

    def resetResizeTime(self):
        for c in self.Controls:
            c.setResizeTime()
#ControlsFrame END