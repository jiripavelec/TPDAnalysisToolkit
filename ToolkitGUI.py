import tkinter as tk
import tkinter.ttk as ttk

class PlotsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)
    
    def initUI(self, parent):
        self.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        # lbl = ttk.Label(self, text="Plots Frame")
        # lbl.pack(side=tk.LEFT, padx=5, pady=5)

        #todo: use self.frames to create multiple tab-frames for different plot outputs
        tab_control = ttk.Notebook(self)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)

        tab_control.add(tab1,text="first")
        tab_control.add(tab2,text="second")
        tab_control.pack(expand=1,fill='both')


class ControlsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        self.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        lbl = ttk.Label(self, text="Controls Frame")
        lbl.pack(side=tk.LEFT, padx=5, pady=5)

class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        rightFrame = PlotsFrame(self, bg ='white')
        leftFrame = ControlsFrame(self, bg = 'grey')


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame()
    root.mainloop()

if __name__ == '__main__':
    main()

