import tkinter as tk
import tkinter.ttk as ttk

#Chord BEGIN
class Chord(tk.Frame):
    def __init__(self, parent, title='', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
        self.m_row = 0
    
    def setRowIdx(self, rowIndex):
        self.m_row = rowIndex
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
            label = tk.Label(self, text=c.title,
                        #   image=i,
                          compound='center',
                          width=width,
                          bg=self.style['title_bg'],
                          fg=self.style['title_fg'],
                          bd=2, relief='groove')
            
            label.grid(row=row, column=0)
            # label.pack(side=tk.TOP, fill=tk.X, expand=False)
            c.grid(row=row+1, column=0, sticky='nsew')
            c.setRowIdx(row+1)
            # c.pack(side=tk.TOP, fill=tk.X, expand=True)
            c.grid_remove()
            # c.pack_forget()
            row += 2
            
            label.bind('<Button-1>', lambda e,
                       target=c, others=chords: self._click_handler(target,others))
            label.bind('<Enter>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['highlight']))
                       label=label: label.config(bg=self.style['highlight']))
            label.bind('<Leave>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['title_bg']))
                       label=label: label.config(bg=self.style['title_bg']))
        
        chords[0].grid() # start with first chord open
        self.grid_rowconfigure(1, weight=1)

        # chords[0].pack()
                       
    def _click_handler(self, target, chords):
        for chord in chords: #close other chords
            if len(chord.grid_info()) != 0:
                chord.grid_remove()
                self.grid_rowconfigure(chord.m_row,weight=0)
                # chord.pack_forget()
        if len(target.grid_info()) == 0: # open target chord
            target.grid()
            self.grid_rowconfigure(target.m_row,weight=1)
            # target.pack()
        # else:
            # target.grid_remove()
            # target.pack_forget()
#Accordion END

#ControlsFrame BEGIN
class ControlsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        self.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        acc = Accordion(self)
        # first chord
        first_chord = Chord(acc, title='First Chord', bg='white')
        tk.Label(first_chord, text='hello world', bg='white').pack()

        # second chord
        second_chord = Chord(acc, title='Second Chord', bg='white')
        tk.Entry(second_chord).pack()
        tk.Button(second_chord, text='Button').pack()

        # third chord
        third_chord = Chord(acc, title='Third Chord', bg='white')
        tk.Text(third_chord).pack()

        # append list of chords to Accordion instance
        acc.append_chords([first_chord, second_chord, third_chord])
        acc.pack(fill=tk.BOTH, expand=1)
#ControlsFrame END