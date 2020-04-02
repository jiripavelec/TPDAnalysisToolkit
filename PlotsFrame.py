import tkinter as tk
import tkinter.ttk as ttk

from datetime import datetime
import matplotlib as mpl
mpl.use('TkAgg') #mpl backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as anim


#MPLContainer BEGIN
class MPLContainer(tk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.m_title = title
        self.initUI(parent)

    def resizePlot(self, *args, **kwargs):
        # print("Width = " + str(self.winfo_width()))
        # print("Height = " + str(self.winfo_height()))
        now = datetime.now()
        if(not self.plotHidden): #hide the plot if we just started resizing
            self.canvas.get_tk_widget().place_forget()
            self.plotHidden = True
        timeDelta = now - self.resizeDateTime #get timedelta since last resize event
        if(timeDelta.total_seconds()*1000 > 200): #if we stopped resizing, unhide plot
            # self.canvas.get_tk_widget().place_forget()
            self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.INSIDE,height=self.winfo_height(),width=self.winfo_width())
            self.plotHidden = False
        #else do nothing
            

    def initUI(self, parent):
        self.pack(side=tk.TOP, fill = tk.BOTH, expand=True)
        # self.place(anchor="nw",bordermode=tk.INSIDE,height=100,relwidth=100)
        # bck = mpl.get_backend()
        # print("Backendis" + bck)
        self.m_figure = Figure(figsize=(5,5), dpi=96)
        self.m_subplot = self.m_figure.add_subplot(111)
        
        # f = mpl.pyplot.Figure(figsize=(5,5), dpi=96)
        # a = f.add_subplot(111)#111 means only one chart as opposed to 121 meanign 2
        self.m_subplot.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        #normally plt.show() now, but different for tk
        self.canvas = FigureCanvasTkAgg(self.m_figure,self)
        self.canvas.draw()
        # canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        # canvas.get_tk_widget().grid(row=0,column=0,sticky="nsew")
        self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.INSIDE,height=200,width=200)
        # self.grid_rowconfigure(index=0,weight=1,minsize=self.winfo_height())
        # self.grid_columnconfigure(index=0,weight=1,minsize=self.winfo_width())
        # self.pack_propagate(0)#should stop grid resizing
        self.resizeDateTime = datetime.now()
        self.plotHidden = False

        self.resizeAnimation = anim.FuncAnimation(self.m_figure, func=self.resizePlot, interval=400)#interval in milliseconds
    
    

        # self.grid_rowconfigure(index=0,minsize=self.winfo_height())
        # self.grid_columnconfigure(index=0,minsize=self.winfo_width())

    # def animate(self,plot):
        
#MPLContainer END

#PlotsFrame BEGIN
class PlotsFrame(tk.Frame):
    # notebooks = {}
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        self.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        # lbl = ttk.Label(self, text="Plots Frame")
        # lbl.pack(side=tk.LEFT, padx=5, pady=5)

        #todo: use self.frames to create multiple tab-frames for different plot outputs
        # self.tab_control = ttk.Notebook(self)
        # self.tab1 = MPLContainer(self.tab_control, bg="white")
        # self.tab2 = ttk.Frame(self.tab_control)

        # self.tab_control.add(self.tab1,text="first")
        # self.tab_control.add(self.tab2,text="second")
        # self.tab_control.pack(expand=1,fill='both')

    # def resizeTest(self):
    #     self.tab1.resizePlot()
#PlotsFrame END
