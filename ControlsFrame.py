import tkinter as tk
import tkinter.ttk as ttk
from DataControls.ControlElements import Accordion
from DataControls.CoverageCalibrationControl import CoverageCalibrationControl
from DataControls.ProcessRawDataControl import ProcessRawDataControl
from DataControls.InvertDataControl import InvertDataControl
from DataControls.RedheadAnalysisControl import RedheadAnalysisControl
from DataControls.PeakIntegrationControl import PeakIntegrationControl

#ControlsFrame BEGIN
class ControlsFrame(tk.Frame):
    def __init__(self, parent, root, plotsFrame, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        self.Controls = []
        self.initUI(plotsFrame, root)

    def initUI(self, plotsFrame, root):
        self.m_accordion = Accordion(self)
        #The order in which we append controls here is also the order in which they show up in the accordion in the UI.

        #For raw data processing
        self.m_rawDataControl = ProcessRawDataControl(plotsFrame, root, self.m_accordion)
        self.Controls.append(self.m_rawDataControl)
        
        #For peak integration
        self.m_peakIntegrationControl = PeakIntegrationControl(plotsFrame, root, self.m_accordion)
        self.Controls.append(self.m_peakIntegrationControl)

        #For inversion of processed data
        self.m_invertDataControl = InvertDataControl(plotsFrame, root, self.m_accordion)
        self.Controls.append(self.m_invertDataControl)

        #For coverage calibration
        self.m_coverageCalibrationControl = CoverageCalibrationControl(plotsFrame, root, self.m_accordion)
        self.Controls.append(self.m_coverageCalibrationControl)

        #For redhead analysis
        self.m_redheadAnalysisControl = RedheadAnalysisControl(plotsFrame, root, self.m_accordion)
        self.Controls.append(self.m_redheadAnalysisControl)

        #separator for easier displaying
        self.m_separator = ttk.Separator(self)
        self.m_separator.pack(side = tk.RIGHT, fill= tk.Y)

    # def initChords(self,plotsFrame, root):
        self.m_startingChordIndex = 0

        for c in self.Controls:
            c.initNotebook(root)
            c.initChordUI()
        self.m_accordion.append_chords(self.m_startingChordIndex,[c.m_chord for c in self.Controls])
        self.m_accordion.pack(side = tk.LEFT, fill=tk.BOTH, expand = True)

        self.setupChordWidths()

    def resetResizeTime(self):
        for c in self.Controls:
            c.setResizeTime()

    def getMinWidth(self):
        reqwidth = max([c.m_chord.getContentWidth() for c in self.Controls])
        return reqwidth

    def setupChordWidths(self):
        reqwidth = max([c.m_chord.getContentWidth() for c in self.Controls])
        for c in self.Controls:
            c.m_chord.setContentWidth(reqwidth)
#ControlsFrame END