import tkinter as tk
import tkinter.ttk as ttk
import operator

from datetime import datetime
import matplotlib as mpl
mpl.use('TkAgg') #mpl backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import backend_bases
# mpl.rcParams['toolbar'] = 'None'
backend_bases.NavigationToolbar2.toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )

from matplotlib.figure import Figure
import matplotlib.animation as anim


#MPLContainer BEGIN
class MPLContainer(tk.Frame):
    def __init__(self, parent, title, yAxisName, xAxisName, secondaryAxis = False, secondaryYAxisName = "" , invertXAxis = False, *args, **kwargs):
        super().__init__(parent, bg="white", *args, **kwargs)
        self.m_title = title
        self.m_xAxisName = xAxisName
        self.m_yAxisName = yAxisName
        self.m_usingMarkers = False
        self.m_secondaryAxisRequired = secondaryAxis
        if(secondaryAxis and secondaryYAxisName == ""):
            raise ValueError #need a secondaryYAxisName!
        self.m_secondaryYAxisName = secondaryYAxisName
        self.m_invertXAxis = invertXAxis
        self.initUI(parent)

    def resizePlot(self, *args, **kwargs):
        now = datetime.now()
        if(not self.plotHidden): #hide the plot if we just started resizing
            # self.canvas.begin_updates()
            self.canvas.get_tk_widget().place_forget()
            self.m_figure.set_dpi(4)#setting figure to lowest dpi possible while hidden, because matplotlib tkagg backend keeps updating figure on resize, even while hidden :(
            # self.canvas.get_tk_widget().pack_forget()
            # self.canvas.get_tk_widget().grid_forget()
            self.plotHidden = True
        timeDelta = now - self.resizeDateTime #get timedelta since last resize event
        if(timeDelta.total_seconds()*1000 > 500): #if we stopped resizing, unhide plot
            # self.canvas.get_tk_widget().place_forget()
            self.m_figure.set_dpi(96)
            self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.OUTSIDE,height=self.winfo_height(),width=self.winfo_width())
            # self.canvas.end_updates()
            # self.canvas.flush_events()
            # self.canvas.get_tk_widget().pack(side=tk.TOP, fill = tk.BOTH, expand = True)
            # self.canvas.get_tk_widget().grid(sticky = "nsew", row = 0, column = 0)
            self.plotHidden = False
        #else do nothing
            

    def initUI(self, parent):
        self.pack(side=tk.TOP, fill = tk.BOTH, expand=True)

        self.m_figure = Figure( dpi=96)
        self.m_subplot = self.m_figure.add_subplot(111) #add_subplot returns axes
        # a = f.add_subplot(111)#111 means only one chart as opposed to 121 meanign 2

        self.m_subplot.set_title(self.m_title)
        self.m_subplot.set_xlabel(self.m_xAxisName)
        self.m_subplot.set_ylabel(self.m_yAxisName)
        self.m_subplot.tick_params(direction="in")
        if(self.m_invertXAxis):
            self.m_subplot.invert_xaxis()

        if(self.m_secondaryAxisRequired):
            self.m_secondaryAxis = self.m_subplot.twinx()
            self.m_secondaryAxis.set_ylabel(self.m_secondaryYAxisName)
            self.m_secondaryAxis.tick_params(direction="in")
        
        #normally plt.show() now, but different for tk
        self.canvas = FigureCanvasTkAgg(self.m_figure,self)
        self.canvas.draw()
        # canvas.get_tk_widget().grid(row=0,column=0,sticky="nsew")
        # self.grid_rowconfigure(index=0,weight=1,minsize=self.winfo_height())
        # self.grid_columnconfigure(index=0,weight=1,minsize=self.winfo_width())
        # self.canvas.get_tk_widget().grid(sticky = "nsew", row = 0, column = 0)
        # self.pack_propagate(0)#should stop grid resizing
        self.resizeDateTime = datetime.now()
        self.plotHidden = False
        self.m_toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.m_toolbar.update()
        # self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        # self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.OUTSIDE,height=self.winfo_height(),width=self.winfo_width())
        self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.INSIDE,relheight = 1.0, relwidth = 1.0)

        self.resizeAnimation = anim.FuncAnimation(self.m_figure, func=self.resizePlot, interval=1000)#, blit = True)#interval in milliseconds
    
    def clearPlots(self):
        if(len(self.m_subplot.lines) > 0):
            for i in range(len(self.m_subplot.lines)-1,-1,-1):
                line = self.m_subplot.lines.pop(i)
                del line
        if(self.m_secondaryAxisRequired):
            if(len(self.m_secondaryAxis.lines) > 0):
                for i in range(len(self.m_secondaryAxis.lines)-1,-1,-1):
                    line = self.m_secondaryAxis.lines.pop(i)
                    del line

    def __switchToMarkers(self, axes):
        for child in axes.get_children():
            if(type(child) is mpl.lines.Line2D):
                child.set_linestyle('None')
                child.set_marker('+')

    def switchToMarkers(self):
        self.__switchToMarkers(self.m_subplot)
        if(self.m_secondaryAxisRequired):
            self.__switchToMarkers(self.m_secondaryAxis)

    def __switchToLines(self, axes):
        for child in axes.get_children():
            if(type(child) is mpl.lines.Line2D):
                child.set_marker('None')
                child.set_linestyle('solid')

    def switchToLines(self):
        self.__switchToLines(self.m_subplot)
        if(self.m_secondaryAxisRequired):
            self.__switchToLines(self.m_secondaryAxis)

    def toggleMarkers(self):
        if(self.m_usingMarkers):
            self.switchToLines()
            self.m_usingMarkers = False
        else:
            self.switchToMarkers()
            self.m_usingMarkers = True

    def __addLinePlots(self, axes, ndarrayData, labels, logXAxis, logYAxis, pLineWidth = 0.75):
        if ndarrayData.ndim >= 2:
            for i in range(1,ndarrayData.shape[0]):
                if (type(labels) is str):
                    axes.plot(ndarrayData[0,:],ndarrayData[i,:], label = labels, linewidth=pLineWidth)
                elif(labels != None):
                    axes.plot(ndarrayData[0,:],ndarrayData[i,:], label = labels[i-1], linewidth=pLineWidth)
                else:
                    axes.plot(ndarrayData[0,:],ndarrayData[i,:], linewidth=pLineWidth)

        if(self.m_usingMarkers):
            self.switchToMarkers() #because we plot with lines by default when adding or subtracting lines

        if (labels != None):
            handles, labels = self.m_subplot.get_legend_handles_labels()
            if(self.m_secondaryAxisRequired):
                handles2, labels2 = self.m_secondaryAxis.get_legend_handles_labels()
                handles = handles + handles2
                labels = labels + labels2
            # reverse the order
            #self.m_subplot.legend(handles[::-1], labels[::-1])

            # or sort them by labels
            hl = sorted(zip(handles, labels),
                        key=operator.itemgetter(1))
            handles2, labels2 = zip(*hl)
            self.m_subplot.legend(handles2, labels2)

        if (logXAxis):
            axes.set_xscale("log")
        if (logYAxis):
            axes.set_yscale("log")
            # axes.set_ylim(bottom=0)

        axes.relim()

    def addPrimaryLinePlots(self, ndarrayData, labels = None, logXAxis = False, logYAxis = False):
        self.__addLinePlots(self.m_subplot, ndarrayData, labels, logXAxis, logYAxis)

    def addSecondaryLinePlots(self, ndarrayData, labels = None, logXAxis = False, logYAxis = False):
        if(not self.m_secondaryAxisRequired):
            raise NameError #should use primary line plots, since secondary axis is not defined for this plot
        self.__addLinePlots(self.m_secondaryAxis, ndarrayData, labels, logXAxis, logYAxis)
        
    def setBottomYLimitZero(self):
        self.m_subplot.set_ylim(bottom=0)


#MPLContainer END

#PlotsFrame BEGIN
class PlotsFrame(tk.Frame):
    # notebooks = {}
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        # self.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
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
