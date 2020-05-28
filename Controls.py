import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
# from PlotsFrame import * 


#Chord BEGIN
class Chord(ttk.Frame):
    def __init__(self, parent, controlRef, title='', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
        self.m_row = 0
        self.controlRef = controlRef
        self.m_label = ""

        #creating scrollable content container here
        self.m_canvas = tk.Canvas(self)
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
        self.m_canvas.pack(side="left", fill="y", expand=True)


    def setRowIdx(self, rowIndex):
        self.m_row = rowIndex

    def onClickedEvent(self):
        self.controlRef.tkraise()
    
#Chord END

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
        
    def append_chords(self, chords=[]):
        '''pass a [list] of Chords to the Accordion object'''

        self.update_idletasks()
        row = 0
        # width = max([c.winfo_reqwidth() for c in chords])
        width = 50

        for c in chords:
            # i = tk.PhotoImage() # blank image to force Label to use pixel size
            c.m_label = tk.Label(self, text=c.title,
                        #   image=i,
                          compound='center',
                          width=width,
                          bg=self.style['title_bg'],
                          fg=self.style['title_fg'],
                          bd=2, relief='groove')
            
            c.m_label.grid(row=row, column=0, sticky='ew')
            # label.pack(side=tk.TOP, fill=tk.X, expand=False)
            c.grid(row=row+1, column=0, sticky='nsew')
            c.setRowIdx(row+1)
            # c.pack(side=tk.TOP, fill=tk.X, expand=True)
            c.grid_remove()
            # c.pack_forget()
            row += 2
            
            c.m_label.bind('<Button-1>', lambda e,
                       target=c, others=chords: self._click_handler(target,others))
            c.m_label.bind('<Enter>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['highlight']))
                       label=c.m_label: label.config(bg=self.style['highlight']))
            c.m_label.bind('<Leave>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['title_bg']))
                       label=c.m_label: label.config(bg=self.style['title_bg']))
        
        self._click_handler(chords[1],chords) # start with first chord open for debugging purposes
                       
    def _click_handler(self, target, chords):
        for chord in chords: #close other chords
            if len(chord.grid_info()) != 0:
                chord.grid_remove()
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
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.m_scrollbarV = tk.Scrollbar(self, orient=tk.VERTICAL)
        # self.m_scrollbarH = tk.Scrollbar(self, orient=tk.HORIZONTAL)

        # self.m_listBox = tk.Listbox(self, selectmode = tk.EXTENDED, yscrollcommand=self.m_scrollbarV.set, xscrollcommand=self.m_scrollbarH.set)
        self.m_listBox = tk.Listbox(self, selectmode = tk.EXTENDED, yscrollcommand=self.m_scrollbarV.set)
        self.m_scrollbarV.config(command=self.m_listBox.yview)
        # self.m_scrollbarH.config(command=self.m_listBox.xview)

        self.m_scrollbarV.pack(side=tk.RIGHT, fill=tk.Y)
        self.m_listBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # self.m_scrollbarH.pack(side=tk.BOTTOM, fill=tk.X)

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

        self.m_availableMassesLabel = ttk.Label(self, text='Available Masses:')
        self.m_availableMassesLabel.grid(row = 0, column = 0, sticky="nsw")

        self.m_availableMassesListBox = ScrolledListBox(self)
        self.m_availableMassesListBox.grid(row = 1, column = 0, sticky = "nsew")

        self.m_displayButton = ttk.Button(self,text="Diplay Selected >>", state = tk.DISABLED, command=self.showSelectedMasses)
        self.m_displayButton.grid(row = 2, column = 0, sticky = "nsew")

        self.m_displayedMassesLabel = ttk.Label(self, text='Displayed Masses:')
        self.m_displayedMassesLabel.grid(row = 0, column = 1, sticky="nsw")

        self.m_displayedMassesListBox = ScrolledListBox(self)
        self.m_displayedMassesListBox.grid(row = 1, column = 1, sticky = "nsew")

        self.m_hideButton = ttk.Button(self,text="<< Hide Selected", state = tk.DISABLED, command=self.hideSelectedMasses)
        self.m_hideButton.grid(row = 2, column = 1, sticky = "nsew")

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
            else: #get intersection of masses
                self.m_availableMassList = list(set(w.getMassList()) & set(self.m_availableMassList))

        for m in self.m_availableMassList:
            self.m_displayedMassesListBox.insert(0,m)
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    
#EnhancedComboBox END

#ProcessingStepControlBase BEGIN
class ProcessingStepControlBase:
    def __init__(self, title, controller):
        self.m_title = title
        self.m_controller = controller
        self.m_chordInitDone = False
        self.m_notebookInitDone = False
        self.mplContainers = []
        self.m_filesDirectory = ""

    #This is for the controls on the left side of the UI
    def initChordUI(self, parent):
        raise NotImplementedError()

    #This is for the tabs with plots on the right side of the UI
    def initNotebook(self, parent):
        raise NotImplementedError()

    #This is to reduce the update frequency of plot resizing to
    #a frequency lower than that of resize events from the main
    #window
    def setResizeTime(self):
        for c in self.mplContainers:
            c.resizeDateTime = datetime.now()

    def selectFiles(self):
        raise NotImplementedError()

    def deselectFiles(self):
        raise NotImplementedError()

    def processInput(self):
        raise NotImplementedError()

    def plotSelectedMasses(self):
        raise NotImplementedError()

#ProcessingStepControlBase END


