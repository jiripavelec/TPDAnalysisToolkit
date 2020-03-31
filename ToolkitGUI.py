import tkinter as tk
import tkinter.ttk as ttk

class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        leftFrame = tk.Frame(self,bg='blue')
        leftFrame.pack(side = tk.LEFT, fill=tk.BOTH)

        leftlbl = tk.Label(leftFrame, text="Left Frame")
        leftlbl.pack(side=tk.LEFT, padx=5, pady=5)


        rightFrame = tk.Frame(self,bg='red')
        rightFrame.pack(side = tk.RIGHT, fill=tk.BOTH, expand=True)

        rightlbl = tk.Label(rightFrame, text="Right Frame")
        rightlbl.pack(side=tk.LEFT, padx=5, pady=5)


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame()
    root.mainloop()

if __name__ == '__main__':
    main()

