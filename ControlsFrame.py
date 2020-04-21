import tkinter as tk
import tkinter.ttk as ttk
from Controls import Accordion
from ProcessRawDataControl import ProcessRawDataControl
from InvertDataControl import InvertDataControl
from RedheadAnalysisControl import RedheadAnalysisControl

#ControlsFrame BEGIN
class ControlsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        self.Controls = []
        self.initUI(parent)

    def initUI(self, parent):
        self.accordion = Accordion(self)
        
        #For raw data processing
        self.m_rawDataControl = ProcessRawDataControl(self)
        self.Controls.append(self.m_rawDataControl)

        #For inversion of processed data
        self.m_invertDataControl = InvertDataControl(self)
        self.Controls.append(self.m_invertDataControl)

        #For redhead analysis
        self.m_redheadAnalysisControl = RedheadAnalysisControl(self)
        self.Controls.append(self.m_redheadAnalysisControl)

    def initChords(self,plotsFrame):
        for c in self.Controls:
            c.initNotebook(plotsFrame)
            c.initChordUI(self.accordion)
        self.accordion.append_chords([c.m_chord for c in self.Controls])
        self.accordion.pack(fill=tk.BOTH, expand = True)

    # def requestProcessedData(self):
    #     return self.m_rawDataControl.getProcessedData()

    # def registerControl(self, control):
    #     # self.Controls[control.m_title] = control
    #     self.Controls.append(control)

    def resetResizeTime(self):
        for c in self.Controls:
            c.setResizeTime()
#ControlsFrame END