import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
# from dt import timedelta

import matplotlib as mpl
mpl.use('TkAgg') #mpl backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as anim


#MPLContainer BEGIN
class MPLContainer(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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

        self.resizeAnimation = anim.FuncAnimation(self.m_figure, func=self.resizePlot, interval=200)#interval in milliseconds
    
    

        # self.grid_rowconfigure(index=0,minsize=self.winfo_height())
        # self.grid_columnconfigure(index=0,minsize=self.winfo_width())

    # def animate(self,plot):
        
#MPLContainer END

#PlotsFrame BEGIN
class PlotsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        self.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        # lbl = ttk.Label(self, text="Plots Frame")
        # lbl.pack(side=tk.LEFT, padx=5, pady=5)

        #todo: use self.frames to create multiple tab-frames for different plot outputs
        self.tab_control = ttk.Notebook(self)
        self.tab1 = MPLContainer(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1,text="first")
        self.tab_control.add(self.tab2,text="second")
        self.tab_control.pack(expand=1,fill='both')

    def resizeTest(self):
        self.tab1.resizePlot()
#PlotsFrame END

#Chord BEGIN
class Chord(tk.Frame):
    def __init__(self, parent, title='', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
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
            c.grid(row=row+1, column=0, sticky='nsew')
            c.grid_remove()
            row += 2
            
            label.bind('<Button-1>', lambda e,
                       target=c, others=chords: self._click_handler(target,others))
            label.bind('<Enter>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['highlight']))
                       label=label: label.config(bg=self.style['highlight']))
            label.bind('<Leave>', lambda e,
                    #    label=label, i=i: label.config(bg=self.style['title_bg']))
                       label=label: label.config(bg=self.style['title_bg']))
        
        #chords[0].grid() # start with first chord open
                       
    def _click_handler(self, target, chords):
        for chord in chords: #close other chords
            if len(chord.grid_info()) != 0:
                chord.grid_remove()
        if len(target.grid_info()) == 0: # open target chord
            target.grid()
        else:
            target.grid_remove()
#Accordion END

#ControlsFrame BEGIN
#Controls should effectively work like an accordion element
class ControlsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI(parent)

    def initUI(self, parent):
        self.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        lbl = ttk.Label(self, text="Controls Frame")
        lbl.pack(side=tk.TOP, padx=5, pady=5)
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
        acc.pack(fill='both', expand=1)


class MainFrame(tk.Frame):
    def __init__(self):#, parent, controller):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("TPD Toolkit")
        self.pack(fill=tk.BOTH, expand=True)

        self.rightFrame = PlotsFrame(self, bg ='white')
        self.leftFrame = ControlsFrame(self, bg = 'grey')
        self.resizeTimer = datetime.now()
        self.rightFrame.resizeTest()

    # def resizePlots(self):
    #     self.rightFrame.resizeTest()

    def resetResizeTime(self,*args,**kwargs):
        self.rightFrame.tab1.resizeDateTime = datetime.now()
#ControlsFrame END



def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    main = MainFrame()
    root.bind('<Configure>',main.resetResizeTime)
    root.mainloop()

if __name__ == '__main__':
    main()

