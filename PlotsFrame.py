import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import math
import operator
import sys
import DataControls.ControlElements as DCCE

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
        ('Home', 'Reset original view', 'home', 'home_extended'),
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
        self.m_containerRef = parent

    def inputCheckFloatEntry(self, entry):
        if(entry.get() == ''):
            return False
        try:
            float(entry.get())
        except ValueError:
            tk.messagebox.showerror("Advanced Settings Error", "Please make sure all inputs are parseable as floats (i.e. decimal numbers).")
            return False
        return True

    def set_advanced_settings(self):
        self.inputCheckFloatEntry(self.m_yMaxBoundEntry)
        pYMax = float(self.m_yMaxBoundEntry.get())
        self.inputCheckFloatEntry(self.m_yMinBoundEntry)
        pYMin = float(self.m_yMinBoundEntry.get())
        self.m_containerRef.getPrimaryAxes().set_ybound(pYMin, pYMax)

        self.inputCheckFloatEntry(self.m_xMaxBoundEntry)
        pXMax = float(self.m_xMaxBoundEntry.get())
        self.inputCheckFloatEntry(self.m_xMinBoundEntry)
        pXMin = float(self.m_xMinBoundEntry.get())
        self.m_containerRef.getPrimaryAxes().set_xbound(pXMin, pXMax)

        self.m_containerRef.m_subplot.grid(linestyle=':')

        if(self.m_containerRef.m_secondaryYAxisRequired):
            self.inputCheckFloatEntry(self.m_secondYMaxBoundEntry)
            sYMax = float(self.m_secondYMaxBoundEntry.get())
            self.inputCheckFloatEntry(self.m_secondYMinBoundEntry)
            sYMin = float(self.m_secondYMinBoundEntry.get())
            self.m_containerRef.getSecondaryAxes().set_ybound(sYMin, sYMax)

        #TODO: get DPI settings working with tkinter canvas -> currently reverting after a few seconds
        # self.inputCheckFloatEntry(self.m_DPIEntry)
        # newDPI = float(self.m_DPIEntry.get())
        # self.m_figureRef.set_dpi(newDPI)

        # self.m_containerRef.m_subplot.relim()
        self.m_containerRef.canvas.draw_idle()

    def advanced_settings(self):
        self.m_window = tk.Toplevel(self.m_root)
        self.m_window.title("Advanced Figure Options")
        if not sys.platform.startswith('win'):
            self.m_window.configure(bg = "#ececec") #ececec only for mac
        
        self.m_yMaxBoundLabel = ttk.Label(self.m_window, text="Primary Max Y Bound")
        self.m_yMaxBoundLabel.grid(row = 0, column = 0, sticky = "nsw")

        self.m_yMaxBoundEntry = DCCE.EnhancedEntry(self.m_window)
        self.m_yMaxBoundEntry.grid(row = 0, column = 1, sticky= "nsew")
        self.m_yMaxBoundEntry.set(self.m_containerRef.getPrimaryAxes().get_ybound()[1])

        self.m_yMinBoundLabel = ttk.Label(self.m_window, text="Primary Min Y Bound")
        self.m_yMinBoundLabel.grid(row = 1, column = 0, sticky = "nsw")

        self.m_yMinBoundEntry = DCCE.EnhancedEntry(self.m_window)
        self.m_yMinBoundEntry.grid(row = 1, column = 1, sticky= "nsew")
        self.m_yMinBoundEntry.set(self.m_containerRef.getPrimaryAxes().get_ybound()[0])

        self.m_xMaxBoundLabel = ttk.Label(self.m_window, text="Primary Max X Bound")
        self.m_xMaxBoundLabel.grid(row = 2, column = 0, sticky = "nsw")

        self.m_xMaxBoundEntry = DCCE.EnhancedEntry(self.m_window)
        self.m_xMaxBoundEntry.grid(row = 2, column = 1, sticky= "nsew")
        self.m_xMaxBoundEntry.set(self.m_containerRef.getPrimaryAxes().get_xbound()[1])

        self.m_xMinBoundLabel = ttk.Label(self.m_window, text="Primary Min X Bound")
        self.m_xMinBoundLabel.grid(row = 3, column = 0, sticky = "nsw")

        self.m_xMinBoundEntry = DCCE.EnhancedEntry(self.m_window)
        self.m_xMinBoundEntry.grid(row = 3, column = 1, sticky= "nsew")
        self.m_xMinBoundEntry.set(self.m_containerRef.getPrimaryAxes().get_xbound()[0])

        self.m_DPILabel = ttk.Label(self.m_window, text="Figure DPI")
        self.m_DPILabel.grid(row = 4, column = 0, sticky = "nsw")

        self.m_DPIEntry = DCCE.EnhancedEntry(self.m_window)
        self.m_DPIEntry.grid(row = 4, column = 1, sticky= "nsew")
        self.m_DPIEntry.set(self.m_figureRef.get_dpi())

        if(self.m_containerRef.m_secondaryYAxisRequired):
            self.m_secondYMaxBoundLabel = ttk.Label(self.m_window, text="Secondary Max Y Bound")
            self.m_secondYMaxBoundLabel.grid(row = 5, column = 0, sticky = "nsw")

            self.m_secondYMaxBoundEntry = DCCE.EnhancedEntry(self.m_window)
            self.m_secondYMaxBoundEntry.grid(row = 5, column = 1, sticky= "nsew")
            self.m_secondYMaxBoundEntry.set(self.m_containerRef.getSecondaryAxes().get_ybound()[1])

            self.m_secondYMinBoundLabel = ttk.Label(self.m_window, text="Secondary Min Y Bound")
            self.m_secondYMinBoundLabel.grid(row = 6, column = 0, sticky = "nsw")

            self.m_secondYMinBoundEntry = DCCE.EnhancedEntry(self.m_window)
            self.m_secondYMinBoundEntry.grid(row = 6, column = 1, sticky= "nsew")
            self.m_secondYMinBoundEntry.set(self.m_containerRef.getSecondaryAxes().get_ybound()[0])

            self.m_buttonRowIndex = 7
        else:
            self.m_buttonRowIndex = 5

        self.m_setButton = ttk.Button(self.m_window, text = "Set Values", command = self.set_advanced_settings)
        self.m_setButton.grid(row = self.m_buttonRowIndex, columnspan = 2, sticky = "ns")

        # raise NotImplementedError

    def save_figure(self):
        # previousSize = self.m_figureRef.get_size_inches()
        # previousDPI = self.m_figureRef.get_dpi()
        # self.m_figureRef.set_dpi(300) #print quality temporarily
        # self.m_figureRef.set_size_inches(w=13.0/2.54, h=8.0/2.54)#13cm by 8cm
        super().save_figure()
        # self.m_figureRef.set_size_inches(previousSize)
        # self.m_figureRef.set_dpi(previousDPI) #print quality temporarily

    def home_extended(self):
        super().home()


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
        # self.m_primaryMaxX = 0
        # self.m_primaryMaxY = 0
        # self.m_secondaryMaxX = 0
        # self.m_secondaryMaxY = 0
        self.m_verticalLines = list()
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
        if(not self.plotHidden and timeDelta.total_seconds()*1000 < 700): #hide the plot if we just started resizing
            self.hidePlot()
        elif(self.plotHidden and timeDelta.total_seconds()*1000 > 700): #if we stopped resizing, unhide plot
            self.showPlot()
        #else do nothing
    
    def explicitRefresh(self):
        self.canvas.draw()
        if(not self.plotHidden):
            self.hidePlot()
        self.showPlot()
        

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
    
    def clearPlots(self):
        if(len(self.m_subplot.lines) > 0):
            for i in range(len(self.m_subplot.lines)-1,-1,-1):
                line = self.m_subplot.lines.pop(i)
                del line
        if(len(self.m_subplot.patches) > 0):
            for i in range(len(self.m_subplot.patches)-1,-1,-1):
                line = self.m_subplot.patches.pop(i)
                del line
        if(self.m_secondaryYAxisRequired):
            if(len(self.m_secondaryYAxis.lines) > 0):
                for i in range(len(self.m_secondaryYAxis.lines)-1,-1,-1):
                    line = self.m_secondaryYAxis.lines.pop(i)
                    del line
        self.canvas.draw_idle()

    def __switchToMarkers(self, axes):
        for child in axes.get_children():
            if(type(child) is mpl.lines.Line2D):
                child.set_linestyle('None')
                child.set_marker('+')

    def switchToMarkers(self):
        self.__switchToMarkers(self.m_subplot)
        if(self.m_secondaryYAxisRequired):
            self.__switchToMarkers(self.m_secondaryYAxis)
        self.canvas.draw_idle()

    def __switchToLines(self, axes):
        for child in axes.get_children():
            if(type(child) is mpl.lines.Line2D):
                child.set_marker('None')
                child.set_linestyle('solid')

    def switchToLines(self):
        self.__switchToLines(self.m_subplot)
        if(self.m_secondaryYAxisRequired):
            self.__switchToLines(self.m_secondaryYAxis)
        self.canvas.draw_idle()

    def toggleMarkers(self):
        if(self.m_usingMarkers):
            self.switchToLines()
            self.m_usingMarkers = False
        else:
            self.switchToMarkers()
            self.m_usingMarkers = True
        self.canvas.draw_idle()

    def __addLinePlots(self, axes, ndarrayData, labels, logXAxis, logYAxis, color, pLineWidth = 1):
        maxX = 0
        maxY = 0
        minX = 0

        if ndarrayData.ndim >= 2:
            for i in range(1,ndarrayData.shape[0]):
                if (type(labels) is str):
                    axes.plot(ndarrayData[0,:],ndarrayData[i,:], label = labels, linewidth=pLineWidth, color = color)
                elif(labels != None):
                    axes.plot(ndarrayData[0,:],ndarrayData[i,:], label = labels[i-1], linewidth=pLineWidth, color = color)
                else:
                    axes.plot(ndarrayData[0,:],ndarrayData[i,:], linewidth=pLineWidth, color = color)
            for l in axes.lines:
                l_maxX = np.amax(l.get_xdata())
                l_minX = np.amin(l.get_xdata())
                l_maxY = 1.1*np.amax(l.get_ydata())
                maxX = np.amax((maxX,l_maxX))
                maxY = np.amax((maxY,l_maxY))
                minX = np.amax((minX,l_minX))
            axes.set_xbound(minX, maxX)#, top = None)
            axes.set_ybound(0, maxY)#, top = None)
            self.m_subplot.grid(linestyle=':')


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

        if (logXAxis):
            axes.set_xscale("log")
            axes.set_xbound(0, math.log(maxX))#, top = None)
        if (logYAxis):
            axes.set_yscale("log")
            axes.set_ybound(0, math.log(maxY))#, top = None)

        axes.relim()

    def addPrimaryLinePlots(self, ndarrayData, labels = None, logXAxis = False, logYAxis = False, color = None):
        self.__addLinePlots(self.m_subplot, ndarrayData, labels, logXAxis, logYAxis, color)
        self.canvas.draw_idle()


    def addSecondaryLinePlots(self, ndarrayData, labels = None, logXAxis = False, logYAxis = False, color = None):
        if(not self.m_secondaryYAxisRequired):
            raise NameError #should use primary line plots, since secondary axis is not defined for this plot
        self.__addLinePlots(self.m_secondaryYAxis, ndarrayData, labels, logXAxis, logYAxis, color)
        self.canvas.draw_idle()

    def addVerticalLine(self, xValue):
        self.m_verticalLines.append(self.m_subplot.axvline(xValue, linestyle="-.", color="r"))
        self.canvas.draw_idle()

    # def removeVerticalLines(self):
    #     if(len(self.m_verticalLines) == 0):
    #         return
    #     for l in self.m_verticalLines:
    #         l.remove() #this function removes the actor from the matplotlib plot, not the list
    #     self.m_verticalLines.clear()

    # def __autoScaleTopY(self):
    #     self.m_subplot.set_ylim(auto = True)
    #     if(self.m_subplot.get_ylim()[0] < 0.0):
    #         self.m_subplot.set_ylim(bottom=0)#, top = None)
    #     self.m_subplot.relim()

    def addSecondaryScaledXAxis(self, forwardFunc, reverseFunc):
        self.m_secondaryScaledXAxis = self.m_subplot.secondary_xaxis("top", functions=(forwardFunc, reverseFunc))
        self.canvas.draw_idle()

    def addSecondaryScaledYAxis(self, forwardFunc, reverseFunc):
        self.m_secondaryScaledXAxis = self.m_subplot.secondary_yaxis("right", functions=(forwardFunc, reverseFunc))
        self.canvas.draw_idle()
    
    def getPrimaryAxes(self):
        return self.m_subplot

    def getSecondaryAxes(self):
        return self.m_secondaryYAxis

    # def setLegendCenterRight(self):
    #     self.m_subplot.get_legend().s

    def shadeBelowCurve(self, x, y, color = "b"):
        self.m_subplot.fill(x,y,color)

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
