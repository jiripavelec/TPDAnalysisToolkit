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
        width = 100

        for c in chords:
            # i = tk.PhotoImage() # blank image to force Label to use pixel size
            c.m_label = tk.Label(self, text=c.title,
                        #   image=i,
                          compound='center',
                        #   width=width,
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
        
        self._click_handler(chords[0],chords)
        # chords[0].grid() # start with first chord open
        # chords[0].onClickedEvent()
        # self.grid_rowconfigure(1, weight=1)

        # chords[0].pack()
                       
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

#ProcessingStepControlBase BEGIN
class ProcessingStepControlBase:
    def __init__(self, title):
        self.m_title = title
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
#ProcessingStepControlBase END


#ControlsFrame BEGIN
class ControlsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        self.initUI(parent)
        self.Controls = []

    def initUI(self, parent):
        self.accordion = Accordion(self)

    def initChords(self,chords):
        self.accordion.append_chords(chords)
        self.accordion.pack(fill=tk.BOTH, expand = True)

    # def registerControl(self, control):
    #     # self.Controls[control.m_title] = control
    #     self.Controls.append(control)

    # def resetResizeTime(self):
    #     for v in self.Controls.values():
    #         v.
#ControlsFrame END