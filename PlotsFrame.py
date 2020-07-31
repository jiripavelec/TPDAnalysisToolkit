import tkinter as tk
import tkinter.ttk as ttk
import operator
import sys
import pyexpat #this is necessary because pyinstaller somehow does not import it, even as a hidden-import

from datetime import datetime
import matplotlib as mpl
mpl.use('TkAgg') #mpl backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import backend_bases
# mpl.rcParams['toolbar'] = 'None'
from matplotlib.figure import Figure
import matplotlib.animation as anim

#Custom MPL Navigation Toolbar BEGIN
class CustomNavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, pFigureCanvasTKAgg, parent, root, *args, **kwargs):
        self.m_root = root
        self.toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
        ('Subplots', 'Configure subplots', 'subplots', 'advanced_settings')
      )
        super().__init__(pFigureCanvasTKAgg, parent, *args, **kwargs)
        self.m_figureRef = pFigureCanvasTKAgg.figure

    def advanced_settings(self):
        self.m_window = tk.Toplevel(self.m_root)
        
        raise NotImplementedError

    def save_figure(self):
        # previousSize = self.m_figureRef.get_size_inches()
        # previousDPI = self.m_figureRef.get_dpi()
        # self.m_figureRef.set_dpi(300) #print quality temporarily
        # self.m_figureRef.set_size_inches(w=13.0/2.54, h=8.0/2.54)#13cm by 8cm
        super().save_figure()
        # self.m_figureRef.set_size_inches(previousSize)
        # self.m_figureRef.set_dpi(previousDPI) #print quality temporarily

#Custom MPL Navigation Toolbar END

#MPLContainer BEGIN
# resizeFuncCounter = 0 #debug
# lastFuncCounterOutputTime = datetime.now() #debug

class MPLContainer(tk.Frame):
    def __init__(self, parent, title, yAxisName, xAxisName, root, secondaryYAxis = False, secondaryYAxisName = "", invertXAxis = False, legendLoc = 0, *args, **kwargs):
        super().__init__(parent, bg="white", *args, **kwargs)
        self.m_title = title
        self.m_xAxisName = xAxisName
        self.m_yAxisName = yAxisName
        self.m_usingMarkers = False
        self.m_legendLoc = legendLoc
        root.registerResizeCallback(self.resizePlot)

        self.m_secondaryYAxisRequired = secondaryYAxis
        if(secondaryYAxis and secondaryYAxisName == ""):
            raise ValueError #need a secondaryYAxisName!
        self.m_secondaryYAxisName = secondaryYAxisName

        self.m_invertXAxis = invertXAxis
        self.initUI(parent, root)

    def hidePlot(self):
        self.canvas.get_tk_widget().place_forget()
        self.m_figure.set_dpi(4)#setting figure to lowest dpi possible while hidden, because matplotlib tkagg backend keeps updating figure on resize, even while hidden :(
        self.plotHidden = True

    def showPlot(self):
            self.m_figure.set_dpi(96)
            self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.OUTSIDE,height=self.winfo_height(),width=self.winfo_width())
            self.plotHidden = False

    def resizePlot(self, timeDelta, *args, **kwargs):
        #resizeFuncCounter related things are for debug output
        # global resizeFuncCounter
        # global lastFuncCounterOutputTime
        # resizeFuncCounter = resizeFuncCounter + 1
        # now = datetime.now()
        
        # outputTimeDelta = now - lastFuncCounterOutputTime
        # if(outputTimeDelta.total_seconds()*1000 > 1000):
        #     print(str(resizeFuncCounter/(outputTimeDelta.total_seconds())) + "resizeFunc calls last second")
        #     resizeFuncCounter = 0
        #     lastFuncCounterOutputTime = datetime.now()

        # timeDelta = now - self.resizeDateTime #get timedelta since last resize event
        if(not self.plotHidden and timeDelta.total_seconds()*1000 < 700): #hide the plot if we just started resizing
            self.hidePlot()
        elif(self.plotHidden and timeDelta.total_seconds()*1000 > 700): #if we stopped resizing, unhide plot
            self.showPlot()
        #else do nothing
    
    def explicitRefresh(self):
        if(not self.plotHidden):
            self.hidePlot()
        self.showPlot()
        # self.canvas.draw()
        

    def initUI(self, parent, root):
        self.pack(side=tk.TOP, fill = tk.BOTH, expand=True)

        self.m_figure = Figure( dpi=96)
        self.m_subplot = self.m_figure.add_subplot(111) #add_subplot returns axes
        # a = f.add_subplot(111)#111 means only one chart as opposed to 121 meanign 2

        self.m_subplot.set_title(self.m_title)
        self.m_subplot.set_xlabel(self.m_xAxisName)
        self.m_subplot.set_ylabel(self.m_yAxisName)
        self.m_subplot.tick_params(direction="in")
        self.m_subplot.grid(linestyle=':')
        self.m_subplot.margins(x = 0.0)
        if(self.m_invertXAxis):
            self.m_subplot.invert_xaxis()

        if(self.m_secondaryYAxisRequired):
            self.m_secondaryYAxis = self.m_subplot.twinx()
            self.m_secondaryYAxis.set_ylabel(self.m_secondaryYAxisName)
            self.m_secondaryYAxis.tick_params(direction="in")
            self.m_secondaryYAxis.margins(x= 0.0)

        #normally plt.show() now, but different for tk
        self.canvas = FigureCanvasTkAgg(self.m_figure,self)
        self.canvas.draw()
        # self.canvas.draw_idle()
        # canvas.get_tk_widget().grid(row=0,column=0,sticky="nsew")
        # self.grid_rowconfigure(index=0,weight=1,minsize=self.winfo_height())
        # self.grid_columnconfigure(index=0,weight=1,minsize=self.winfo_width())
        # self.canvas.get_tk_widget().grid(sticky = "nsew", row = 0, column = 0)
        # self.pack_propagate(0)#should stop grid resizing
        self.resizeDateTime = datetime.now()
        self.plotHidden = False
        self.m_toolbar = CustomNavigationToolbar(self.canvas, self, root)
        self.m_toolbar.update()
        # self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        # self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.OUTSIDE,height=self.winfo_height(),width=self.winfo_width())
        self.canvas.get_tk_widget().place(anchor="nw",bordermode=tk.INSIDE,relheight = 1.0, relwidth = 1.0)

        # if not sys.platform.startswith('win'):
        # self.resizeAnimation = anim.FuncAnimation(self.m_figure, func=self.resizePlot, interval=300, cache_frame_data=False)#, blit = True)#interval in milliseconds
    
    def clearPlots(self):
        if(len(self.m_subplot.lines) > 0):
            for i in range(len(self.m_subplot.lines)-1,-1,-1):
                line = self.m_subplot.lines.pop(i)
                del line
        if(self.m_secondaryYAxisRequired):
            if(len(self.m_secondaryYAxis.lines) > 0):
                for i in range(len(self.m_secondaryYAxis.lines)-1,-1,-1):
                    line = self.m_secondaryYAxis.lines.pop(i)
                    del line
        self.canvas.draw()

    def __switchToMarkers(self, axes):
        for child in axes.get_children():
            if(type(child) is mpl.lines.Line2D):
                child.set_linestyle('None')
                child.set_marker('+')

    def switchToMarkers(self):
        self.__switchToMarkers(self.m_subplot)
        if(self.m_secondaryYAxisRequired):
            self.__switchToMarkers(self.m_secondaryYAxis)
        self.canvas.draw()

    def __switchToLines(self, axes):
        for child in axes.get_children():
            if(type(child) is mpl.lines.Line2D):
                child.set_marker('None')
                child.set_linestyle('solid')

    def switchToLines(self):
        self.__switchToLines(self.m_subplot)
        if(self.m_secondaryYAxisRequired):
            self.__switchToLines(self.m_secondaryYAxis)
        self.canvas.draw()

    def toggleMarkers(self):
        if(self.m_usingMarkers):
            self.switchToLines()
            self.m_usingMarkers = False
        else:
            self.switchToMarkers()
            self.m_usingMarkers = True
        self.canvas.draw()

    def __addLinePlots(self, axes, ndarrayData, labels, logXAxis, logYAxis, pLineWidth = 1):
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
            if(self.m_secondaryYAxisRequired):
                handles2, labels2 = self.m_secondaryYAxis.get_legend_handles_labels()
                handles = handles + handles2
                labels = labels + labels2
            # reverse the order
            #self.m_subplot.legend(handles[::-1], labels[::-1])

            # or sort them by labels
            hl = sorted(zip(handles, labels),
                        key=operator.itemgetter(1))
            handles, labels = zip(*hl)
            legend = self.m_subplot.legend(handles, labels, loc=self.m_legendLoc)
            # if(self.m_secondaryYAxisRequired):
            #     legend.remove()
            #     self.m_secondaryYAxis.add_artist(legend)

        if (logXAxis):
            axes.set_xscale("log")
        if (logYAxis):
            axes.set_yscale("log")
            # axes.set_ylim(bottom=0)

        axes.relim()

    def addPrimaryLinePlots(self, ndarrayData, labels = None, logXAxis = False, logYAxis = False):
        self.__addLinePlots(self.m_subplot, ndarrayData, labels, logXAxis, logYAxis)
        self.__autoScaleTopY()
        self.canvas.draw()
        # self.canvas.draw_idle()


    def addSecondaryLinePlots(self, ndarrayData, labels = None, logXAxis = False, logYAxis = False):
        if(not self.m_secondaryYAxisRequired):
            raise NameError #should use primary line plots, since secondary axis is not defined for this plot
        self.__addLinePlots(self.m_secondaryYAxis, ndarrayData, labels, logXAxis, logYAxis)
        self.canvas.draw()
        # self.canvas.draw_idle()

        
    def __autoScaleTopY(self):
        self.m_subplot.set_ylim(auto = True)
        if(self.m_subplot.get_ylim()[0] < 0.0):
            self.m_subplot.set_ylim(bottom=0, top = None)

    def addSecondaryScaledXAxis(self, forwardFunc, reverseFunc):
        self.m_secondaryScaledXAxis = self.m_subplot.secondary_xaxis("top", functions=(forwardFunc, reverseFunc))
        self.canvas.draw()

    def addSecondaryScaledYAxis(self, forwardFunc, reverseFunc):
        self.m_secondaryScaledXAxis = self.m_subplot.secondary_yaxis("right", functions=(forwardFunc, reverseFunc))
        self.canvas.draw()
        
    # def setLegendCenterRight(self):
    #     self.m_subplot.get_legend().s

#MPLContainer END

#PlotsFrame BEGIN
class PlotsFrame(tk.Frame):
    # notebooks = {}
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)
        self.m_notebooks = {}

    def initUI(self, parent):
        # self.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)

    def requestNotebook(self, key):
        self.m_notebooks[key] = ttk.Notebook(self)
        self.m_notebooks[key].grid(row=0,column=0,sticky="nsew") #initalize
        self.m_notebooks[key].grid_forget() #but hide right away
        return self.m_notebooks[key]

    def raiseNotebook(self, key):
        self.m_notebooks[key].grid(row=0,column=0,sticky="nsew")

    def hideNotebook(self, key):
        self.m_notebooks[key].grid_forget()

#PlotsFrame END
