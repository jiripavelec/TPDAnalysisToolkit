import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import * #ui element
from PlotsFrame import PlotsFrame

# from dt import timedelta

class ProcessingStepControls:
    def __init__(self, title):
        self.m_title = title
        self.m_chordInitDone = False
        self.m_notebookInitDone = False
        self.mplContainers = []

    def initChordUI(self, parent):
        raise NotImplementedError()


    # def getControlChord(self,parent, plotsFrame):
    #     if(not self.m_chordInitDone):
    #         self.m_chord = Chord(parent, self.getNotebook(plotsFrame), title=self.m_title)
    #         self.initChordUI()

    #     return self.m_chord

    def initNotebook(self, parent):
        raise NotImplementedError()

    # def getNotebook(self,parent):
    #     if(not self.m_notebookInitDone):
    #         self.m_notebook = ttk.Notebook(parent)
    #         self.initNotebook()

    #     return self.m_notebook

    # def chordWasClicked(self, chord):
    #     self.m_notebook.tkraise()

    def setResizeTime(self):
        for c in self.mplContainers:
            c.resizeDateTime = datetime.now()

class ProcessTPDData(ProcessingStepControls):
    def __init__(self):
        super().__init__("Process TPD Data")


    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "First graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Second graph", bg="white"))
        # self.tab1 = MPLContainer(self.m_notebook, bg="white")
        # self.tab2 = ttk.Frame(self.m_notebook)
        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)
        # self.m_notebook.add(self.tab1,text="first")
        # self.m_notebook.add(self.tab2,text="second")
        # self.m_notebook.pack(expand=1,fill='both')
        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)
        tk.Label(self.m_chord, text='hello world', bg='white').pack()

class InvertTPDData(ProcessingStepControls):
    def __init__(self):
        super().__init__("Invert TPD Data (Inversion Analysis Step #1)")

    def initNotebook(self, parent):
        self.m_notebook = ttk.Notebook(parent)

        self.mplContainers.append(MPLContainer(self.m_notebook, "First graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Second graph", bg="white"))
        self.mplContainers.append(MPLContainer(self.m_notebook, "Third graph", bg="white"))
        # self.tab1 = MPLContainer(self.m_notebook, bg="white")
        # self.tab2 = ttk.Frame(self.m_notebook)
        for c in self.mplContainers:
            self.m_notebook.add(c, text = c.m_title)
        # self.m_notebook.add(self.tab1,text="first")
        # self.m_notebook.add(self.tab2,text="second")
        # self.m_notebook.pack(expand=1,fill='both')
        self.m_notebook.grid(row=0,column=0,sticky="nsew")

    def initChordUI(self, parent):
        self.m_chord = Chord(parent, self.m_notebook, title=self.m_title)
        tk.Label(self.m_chord, text='hello world, I am different!', bg='white').pack()



class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.ControlArray = []
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        self.ControlArray.append(ProcessTPDData())
        self.ControlArray.append(InvertTPDData())

        self.plotsFrame = PlotsFrame(self, bg ='white')
        self.controlsFrame = ControlsFrame(self, bg = 'grey')
        
        for c in self.ControlArray:
            c.initNotebook(self.plotsFrame)
            c.initChordUI(self.controlsFrame.accordion)

        self.controlsFrame.initChords([c.m_chord for c in self.ControlArray])

        self.resizeTimer = datetime.now()
        # self.rightFrame.resizeTest()
        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()
    # def resizePlots(self):
    #     self.rightFrame.resizeTest()

    def resetResizeTime(self,*args,**kwargs):
        # if( (not (self.lastWidth == self.winfo_width)) or (not (self.lastHeight == self.winfo_height))):
        for c in self.ControlArray:
            c.setResizeTime()
        # self.leftFrame.Controls.m_notebook.resizeDateTime = datetime.now()
        self.lastWidth = self.winfo_width
        self.lastHeight = self.winfo_height
        #else we didnt resize as the dimensions have not changed


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame()
    root.bind('<Configure>',main.resetResizeTime)
    root.mainloop()

if __name__ == '__main__':
    main()

