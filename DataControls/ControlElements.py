import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory, askopenfilenames, asksaveasfilename, askopenfilename
import os.path
from os import path, chdir
from datetime import datetime
import sys
# from PlotsFrame import MPLContainer # pylint: disable=import-error


#Chord BEGIN
class Chord(ttk.Frame):
    def __init__(self, parent, controller, title='', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.m_title = title
        self.m_row = 0
        self.m_controller = controller
        self.m_label = ""

        #creating scrollable content container here
        if sys.platform.startswith('win'):
            self.m_canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        else:
            self.m_canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg = "#ececec") #ececec only for mac
        self.m_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.m_canvas.yview)
        self.m_scrollable_frame = ttk.Frame(self.m_canvas)
        self.m_scrollable_frame.bind(
                "<Configure>",
                lambda e: self.m_canvas.configure(
                    scrollregion=self.m_canvas.bbox("all")
                )
            )
        self.m_canvas.create_window((0, 0), window=self.m_scrollable_frame, anchor="nw")
        self.m_canvas.configure(yscrollcommand=self.m_scrollbar.set)

        self.m_scrollbar.pack(side="left", fill="y")
        self.m_canvas.pack(side="left", fill = "both", expand=True)
        self.m_notebookRef = self.m_controller.requestNotebook(self.m_title)

    def setRowIdx(self, rowIndex):
        self.m_row = rowIndex

    def onClickedEvent(self):
        self.m_controller.raiseNotebook(self.m_title)
        tabName = self.m_notebookRef.select()
        if tabName:
            plot = self.m_notebookRef.nametowidget(tabName)
            plot.explicitRefresh()

    def hideNotebook(self):
        self.m_controller.hideNotebook(self.m_title)
    
    def getContentWidth(self):
        # return max([c.winfo_reqwidth() for c in self.m_scrollable_frame.winfo_children()])
        return self.m_scrollable_frame.winfo_reqwidth() + self.m_scrollbar.winfo_reqwidth()
    
    def setContentWidth(self, width):
        self.configure(width = width)
        self.m_canvas.configure(width = width - self.m_scrollbar.winfo_reqwidth())
        self.m_scrollable_frame.configure(width = width - self.m_scrollbar.winfo_reqwidth())
    
#Chord END

#WrappedLabel BEGIN
class WrappedLabel(ttk.Frame):
    def __init__(self, parent, text, compound, width, bg, fg, bd, relief, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.m_label = tk.Label(self, text = text, compound=compound, bg=bg, fg=fg, bd=bd, relief=relief)
        self.m_label.pack(side = tk.TOP, fill=tk.BOTH, expand = True)

#WrappedLabel END

#Accordion BEGIN
#adapted from http://code.activestate.com/recipes/578911-accordion-widget-tkinter/
class Accordion(tk.Frame):
    def __init__(self, parent, accordion_style=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # if no style dict, assign default style
        if accordion_style:
            self.style = accordion_style
        else:
            self.style = accordion_style = {
                'title_bg': 'white',
                'title_fg': 'black',
                'highlight': 'white smoke'
                }
        
        self.columnconfigure(0, weight=1)
        
    def append_chords(self, startingChord, chords=[]):
        '''pass a [list] of Chords to the Accordion object'''

        self.update_idletasks()
        row = 0
        #reqwidth = max([c.getContentWidth() for c in chords])
        # width = 55
        # self.configure(width = reqwidth)

        for c in chords:
            # i = tk.PhotoImage() # blank image to force Label to use pixel size
            c.m_label = tk.Label(self, text=c.m_title,
            # c.m_label = WrappedLabel(self, text=c.m_title,
                        #   image=i,
                          compound='center',
                        #   width=width,
                        #   width=reqwidth,
                          bg=self.style['title_bg'],
                          fg=self.style['title_fg'],
                          bd=2, relief='groove')
            
            c.m_label.grid(row=row, column=0, sticky='ew')
            # c.m_label.grid_propagate(0)
            # label.pack(side=tk.TOP, fill=tk.X, expand=False)
            c.grid(row=row+1, column=0, sticky='nsew')
            c.setRowIdx(row+1)
            # c.pack(side=tk.TOP, fill=tk.X, expand=True)
            c.grid_remove()
            # c.pack_forget()
            row += 2
            
            c.m_label.bind('<Button-1>', lambda e,
            # c.m_label.m_label.bind('<Button-1>', lambda e,
                       target=c, others=chords: self._click_handler(target,others))
            c.m_label.bind('<Enter>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['highlight']))
                       label=c.m_label: label.config(bg=self.style['highlight']))
                    #    label=c.m_label: label.m_label.config(bg=self.style['highlight']))
            c.m_label.bind('<Leave>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['title_bg']))
                       label=c.m_label: label.config(bg=self.style['title_bg']))
                    #    label=c.m_label: label.m_label.config(bg=self.style['title_bg']))
        
        self._click_handler(chords[startingChord],chords) # start with first chord open for debugging purposes
                       
    def _click_handler(self, target, chords):
        for chord in chords: #close other chords
            if (len(chord.grid_info()) != 0) and (chord != target):
                chord.grid_remove()
                chord.hideNotebook()
                self.grid_rowconfigure(chord.m_row,weight=0)
                # chord.m_label.config(bg=self.style['title_bg'], fg =self.style['title_fg'])
                # chord.m_label.config(bd=2)
                # chord.pack_forget()
        if len(target.grid_info()) == 0: # open target chord
            target.grid()
            target.onClickedEvent()
            self.grid_rowconfigure(target.m_row,weight=1)
            # target.m_label.config(bg="white")
            # target.m_label.config(bd=0)

            # target.pack()
        # else:
            # target.grid_remove()
            # target.pack_forget()
#Accordion END

#ScrolledListBox BEGIN
class ScrolledListBox(ttk.Frame):
    def __init__(self, parent, horizontallyScrollable = False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        if(horizontallyScrollable):
            self.m_internalFrame = ttk.Frame(self)
            self.m_scrollbarV = tk.Scrollbar(self.m_internalFrame, orient=tk.VERTICAL)
            self.m_scrollbarH = tk.Scrollbar(self, orient=tk.HORIZONTAL)

            self.m_listBox = tk.Listbox(self.m_internalFrame, selectmode = tk.EXTENDED, yscrollcommand=self.m_scrollbarV.set, xscrollcommand=self.m_scrollbarH.set)
            self.m_scrollbarV.config(command=self.m_listBox.yview)
            self.m_scrollbarH.config(command=self.m_listBox.xview)

            self.m_internalFrame.pack(side=tk.TOP, fill=tk.X)
            self.m_scrollbarV.pack(side=tk.RIGHT, fill=tk.Y)
            self.m_listBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.m_scrollbarH.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.m_scrollbarV = tk.Scrollbar(self, orient=tk.VERTICAL)
            self.m_listBox = tk.Listbox(self, selectmode = tk.EXTENDED, yscrollcommand=self.m_scrollbarV.set)

            self.m_scrollbarV.config(command=self.m_listBox.yview)

            self.m_scrollbarV.pack(side=tk.RIGHT, fill=tk.Y)
            self.m_listBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def insert(self, index, *elements):
        self.m_listBox.insert(index, *elements)

    def clear(self):
        self.m_listBox.delete(0,self.m_listBox.size()-1)

    def delete(self, first, last = None):
        self.m_listBox.delete(first, last)

    def get(self, first, last = None):
        return self.m_listBox.get(first, last)
    
    def size(self):
        return self.m_listBox.size()

    def curselection(self):
        return self.m_listBox.curselection()
#ScrolledListBox END

#EnhancedCheckButton BEGIN
class EnhancedCheckButton(ttk.Checkbutton):
    def __init__(self, parent, *args, **kwargs):
        self.m_var = tk.IntVar()
        self.m_var.set(0)
        super().__init__(parent, var = self.m_var, *args, **kwargs)
        # self.var = self.m_var

    def get(self):
        return self.m_var.get()

    def set(self, value):
        self.m_var.set(value)
#EnhancedCheckButton END

#EnhancedEntry BEGIN
class EnhancedEntry(ttk.Entry):
    def __init__(self, parent, *args, **kwargs):
        self.m_backingVariable = tk.StringVar()
        super().__init__(parent, textvariable = self.m_backingVariable, *args, **kwargs)

    def get(self):
        return self.m_backingVariable.get()

    def set(self, *args, **kwargs):
        self.m_backingVariable.set(*args,**kwargs)

    def setBackingVar(self, value):
        self.m_backingVariable.set(value)

#EnhancedEntry END

#DisplayOptionsFrame BEGIN
class DisplayOptionsFrame(ttk.Frame):
    def __init__(self, parent, onUpdateEventCommand, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.m_availableMassList = []
        self.initUI()
        self.m_onUpdate = onUpdateEventCommand

    def initUI(self):
        self.m_showIntersectionOfMassesCheckBox = EnhancedCheckButton(self, text="Only show masses available across all files")
        self.m_showIntersectionOfMassesCheckBox.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_availableMassesLabel = ttk.Label(self, text='Available Masses:')
        self.m_availableMassesLabel.grid(row = 1, column = 0, sticky="nsw")

        self.m_availableMassesListBox = ScrolledListBox(self)
        self.m_availableMassesListBox.grid(row = 2, column = 0, sticky = "nsew")

        self.m_displayButton = ttk.Button(self,text="Display Selected >>", state = tk.DISABLED, command=self.showSelectedMasses)
        self.m_displayButton.grid(row = 3, column = 0, sticky = "nsew")

        self.m_displayedMassesLabel = ttk.Label(self, text='Displayed Masses:')
        self.m_displayedMassesLabel.grid(row = 1, column = 1, sticky="nsw")

        self.m_displayedMassesListBox = ScrolledListBox(self)
        self.m_displayedMassesListBox.grid(row = 2, column = 1, sticky = "nsew")

        self.m_hideButton = ttk.Button(self,text="<< Hide Selected", state = tk.DISABLED, command=self.hideSelectedMasses)
        self.m_hideButton.grid(row = 3, column = 1, sticky = "nsew")

        self.grid_columnconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=1, weight=1)

    def debugPrintDisplayedMassesListBox(self):
        [print(e) for e in self.m_displayedMassesListBox.get(0,self.m_displayedMassesListBox.size()-1)]

    def updateButtonStates(self):
        if self.m_availableMassesListBox.size() == 0:
            self.m_displayButton.configure(state = tk.DISABLED)
        else:
            self.m_displayButton.configure(state = tk.NORMAL)
        if self.m_displayedMassesListBox.size() == 0:
            self.m_hideButton.configure(state = tk.DISABLED)
        else:
            self.m_hideButton.configure(state = tk.NORMAL)

    def resetMasses(self, rawDataWrappers):
        self.m_availableMassesListBox.clear()
        self.m_availableMassList = []
        self.m_displayedMassesListBox.clear()
        for w in rawDataWrappers:
            if (len(self.m_availableMassList) == 0 and rawDataWrappers.index(w) == 0): #set masses 
                self.m_availableMassList = w.getMassList()
            else:
                if(self.m_showIntersectionOfMassesCheckBox.instate(['!selected'])): #get intersection of masses
                    self.m_availableMassList = list(set(w.getMassList()).union(set(self.m_availableMassList)))
                else: #get union of masses
                    self.m_availableMassList = list(set(w.getMassList()) & set(self.m_availableMassList))

        # self.m_displayedMassesListBox.insert(0,self.m_availableMassList[0])
        # for m in self.m_availableMassList[1:]:
        for m in self.m_availableMassList:
            self.m_availableMassesListBox.insert(0,m)
        self.updateButtonStates()

    def hideSelectedMasses(self):
        selected = list(self.m_displayedMassesListBox.curselection())
        selected.reverse()
        for s in selected:
            self.m_availableMassesListBox.insert(0,self.m_displayedMassesListBox.get(s))
            self.m_displayedMassesListBox.delete(s)
        self.updateButtonStates()
        self.m_onUpdate()

    def showSelectedMasses(self):
        selected = list(self.m_availableMassesListBox.curselection())
        selected.reverse()
        for s in selected:
            self.m_displayedMassesListBox.insert(0,self.m_availableMassesListBox.get(s))
            self.m_availableMassesListBox.delete(s)
        self.updateButtonStates()
        self.m_onUpdate()

    def getMassesToDisplay(self):
        return [e for e in self.m_displayedMassesListBox.get(0,self.m_displayedMassesListBox.size()-1)]

    def getAllMasses(self):
        return self.m_availableMassList

#DisplayOptionsFrame END

#EnhancedComboBox BEGIN
class EnhancedComboBox(ttk.Combobox):
    def __init__(self, textState = "readonly", *args, **kwargs):
        self.m_backingVariable = tk.StringVar()
        super().__init__(textvariable = self.m_backingVariable, state = textState, *args, **kwargs)
    
#EnhancedComboBox END

#ProcessingStepControlBase BEGIN
class ProcessingControlBase:
    def __init__(self, title, controller, accordion):
        self.m_title = title
        self.m_controller = controller
        self.m_chord = Chord(accordion, controller, title)
        self.m_chordInitDone = False
        self.m_notebookInitDone = False
        self.m_plots = {} #Add MPL containers to m_plots

    #This is for the controls on the left side of the UI
    def initChordUI(self):
        raise NotImplementedError()

    #This is for the tabs with plots on the right side of the UI
    def initNotebook(self, root):
        for c in self.m_plots.values():
            self.m_chord.m_notebookRef.add(c, text = c.m_title)
            self.m_chord.m_notebookRef.bind("<<NotebookTabChanged>>", self.onNotebookTabChanged)

    #This is to reduce the update frequency of plot resizing to
    #a frequency lower than that of resize events from the main
    #window
    def setResizeTime(self):
        for c in self.m_plots.values():
            c.resizeDateTime = datetime.now()

    def selectFiles(self):
        raise NotImplementedError()

    def deselectFiles(self):
        raise NotImplementedError()

    def processInput(self):
        raise NotImplementedError()

    def plotSelectedMasses(self):
        raise NotImplementedError()

    def onNotebookTabChanged(self, event):
        selected_tab = event.widget.select()
        event.widget.children[selected_tab.split('.')[-1]].explicitRefresh()
        # for p in self.m_plots.values():
        #     p.explicitRefresh()
                
#ProcessingStepControlBase END

#InputFileListBoxControl BEGIN
class InputFileListBoxControl(ttk.Frame):
    def __init__(self, parent, onUpdateSelection, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.onUpdateSelection = onUpdateSelection
        self.m_filePaths = list()

        self.m_filesListBoxLabel = ttk.Label(self, text='Input files:')
        self.m_filesListBoxLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_filesListBox = ScrolledListBox(self, horizontallyScrollable=True)
        self.m_filesListBox.grid(row = 1, column = 0, columnspan = 4, sticky = "nsew")

        self.m_fileButtonFrame = ttk.Frame(self)
        self.m_fileButtonFrame.grid(row=2, column = 1, columnspan = 3, sticky = "nsew")

        self.m_selectFilesButton = ttk.Button(self.m_fileButtonFrame,text="Add Files",command = self.selectFiles)
        self.m_selectFilesButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_selectFilesButton = ttk.Button(self.m_fileButtonFrame,text="Add Directory",command = self.selectDir)
        self.m_selectFilesButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_deselectButton = ttk.Button(self.m_fileButtonFrame,text="Remove Selected",command = self.deselectFiles)
        self.m_deselectButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.m_filterButton = ttk.Button(self.m_fileButtonFrame,text="Filter for \"TPD\"",command = self.filterForTPD)
        self.m_filterButton.pack(side=tk.RIGHT, fill = tk.X, expand = False)

        self.grid_columnconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=1, weight=1)
        self.grid_columnconfigure(index=2, weight=1)
        self.grid_columnconfigure(index=3, weight=1)

    def filterForTPD(self):
        previousPaths = self.m_filePaths.copy()
        self.m_filePaths.clear()
        for candidate in previousPaths: #look at all paths
            if(candidate.split('/')[-1].find("TPD") != -1): #look for "TPD" in filename to differentiate data from prep files
                self.m_filePaths.append(candidate)
        self.prepareFileSelections()                        

    def prepareFileSelections(self):
        self.m_fileList = list()
        self.m_filesListBox.clear()
        for p in self.m_filePaths:
            substrings = p.split('/')
            fName = substrings[len(substrings) - 1]
            self.m_fileList.insert(0,fName)

        [self.m_filesListBox.insert(0, f) for f in self.m_fileList]
        self.m_fileList.reverse()
        self.onUpdateSelection(self.m_fileList)

    def selectFiles(self):
        buffer = list(askopenfilenames(defaultextension=".csv", filetypes=[('Comma-separated Values','*.csv'), ('All files','*.*')]))
        if not (len(buffer) == 0):
            for p in buffer:
                if p not in self.m_filePaths:
                    self.m_filePaths.append(p) 
            self.prepareFileSelections()

    def selectDir(self):
        dirPath = askdirectory(mustexist = True)
        if not (len(dirPath) == 0):
            self.m_filePaths.clear()
            candidates = os.listdir(dirPath)
            for candidate in candidates: #look at all paths in directory
                if(os.path.isfile(dirPath + '/' + candidate) and candidate.endswith(".csv")): #filter out directories
                    self.m_filePaths.append(dirPath + '/' + candidate)
            self.filterForTPD()

    def deselectFiles(self):
        indices = list(self.m_filesListBox.curselection())
        indices.reverse()
        for i in indices:
            self.m_filesListBox.delete(i)
            self.m_filePaths.pop(i)
            self.m_fileList.pop(i)
        self.onUpdateSelection(self.m_fileList)
        

#InputFileListBoxControl END

#SingleInputFileSelectionControl BEGIN
class SingleInputFileSelectionControl(ttk.Frame):
    def __init__(self, parent, onSelect = None, defaultextension= ".pdat", filetypes = [('Processed Data','*.pdat'), ('All files','*.*')],*args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.m_inputLabel = ttk.Label(self, text='Input file:')
        self.m_inputLabel.grid(row = 0, column = 0, columnspan = 2, sticky="nsw")

        self.m_fileNameLabel = ttk.Label(self, text='No file selected')
        self.m_fileNameLabel.grid(row = 1, column = 1, columnspan = 3, sticky="nsew")

        self.m_selectButton = ttk.Button(self,text="Select File",command = self.selectFile)
        self.m_selectButton.grid(row=2, column = 2, columnspan=1, sticky = "nse")

        self.m_fileTypes = filetypes
        self.m_defaultExtension = defaultextension

        self.m_onSelect = onSelect

    def selectFile(self):
        buffer = askopenfilename(defaultextension= self.m_defaultExtension, filetypes= self.m_fileTypes)
        if (not buffer == None): #we only want a new filepath if it is a valid path
            self.m_inputFilePath = buffer
            substrings = self.m_inputFilePath.split('/')
            self.m_inputFileName = substrings[len(substrings) - 1]
            self.m_fileNameLabel.configure(text = self.m_inputFileName)
            if(self.m_onSelect != None):
                self.m_onSelect()
#SingleInputFileSelectionControl END