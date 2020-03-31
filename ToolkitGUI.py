import tkinter as tk
import tkinter.ttk as ttk

class PlotsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)
    
    def initUI(self, parent):
        self.pack(side = tk.LEFT, fill = tk.BOTH)
        lbl = ttk.Label(self, text="Left Frame")
        lbl.pack(side=tk.LEFT, padx=5, pady=5)


class ControlsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        self.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        lbl = ttk.Label(self, text="Right Frame")
        lbl.pack(side=tk.LEFT, padx=5, pady=5)

class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        # leftFrame = tk.Frame(self,bg = "blue")
        # leftFrame.pack(side = tk.LEFT, fill=tk.BOTH)

        # leftlbl = ttk.Label(leftFrame, text="Left Frame")
        # leftlbl.pack(side=tk.LEFT, padx=5, pady=5)

        leftFrame = PlotsFrame(self, bg ='blue')

        # rightFrame = tk.Frame(self,bg='red')
        # rightFrame.pack(side = tk.RIGHT, fill=tk.BOTH, expand=True)

        # rightlbl = ttk.Label(rightFrame, text="Right Frame")
        # rightlbl.pack(side=tk.LEFT, padx=5, pady=5)

        rightFrame = ControlsFrame(self, bg = 'red')


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame()
    root.mainloop()

if __name__ == '__main__':
    main()

