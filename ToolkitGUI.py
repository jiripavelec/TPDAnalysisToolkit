import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from ControlsFrame import ControlsFrame #ui element
from PlotsFrame import PlotsFrame

# from dt import timedelta

class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        self.rightFrame = PlotsFrame(self, bg ='white')
        self.leftFrame = ControlsFrame(self, bg = 'grey')
        self.resizeTimer = datetime.now()
        # self.rightFrame.resizeTest()
        self.lastWidth = self.winfo_width()
        self.lastHeight = self.winfo_height()
    # def resizePlots(self):
    #     self.rightFrame.resizeTest()

    def resetResizeTime(self,*args,**kwargs):
        if( (not (self.lastWidth == self.winfo_width)) or (not (self.lastHeight == self.winfo_height))):
            self.rightFrame.tab1.resizeDateTime = datetime.now()
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

