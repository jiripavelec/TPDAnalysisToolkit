# from tkinter import *
# from tkinter.ttk import *
import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Hello world!")
    root.geometry('1920x1080')
    
    tab_control = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_control)
    tab2 = ttk.Frame(tab_control)


    tab_control.add(tab1,text="first")
    tab_control.add(tab2,text="second")
    tab_control.pack(expand=1,fill='both')

    lbl = tk.Label(tab1, text="LabelText", font=("Arial Bold", 24))
    lbl.grid(column=0, row=0)
    
    label2 = tk.Label(tab1, text="", font=("Arial Bold", 24))
    label2.grid(column=0,row=1)

    txt = tk.Entry(tab1, width=10)
    txt.grid(column=1,row=1)

    selected = tk.IntVar() #int()
    
    lbl3 = tk.Label(tab1)
    lbl3.grid(column=3,row=3)

    def clicked():
        lbl.configure(text="You clicked me!?!?")
        label2.configure(text=txt.get())
        lbl3.configure(text=selected.get())
    btn = ttk.Button(tab1, text="I am a button", command=clicked)
    btn2 = tk.Button(tab1, text="I am Butohn", command= clicked, relief = 'groove',  padx='20', pady='20')#, highlightbackground='#3E4149')
    # btn2 = ttk.Button(tab1, text="Button2", highlightbackground="red")
    btn.grid(column=1,row=0)
    btn2.grid(column=2,row=0)

    s = ttk.Style()
    s.configure('TButton',
        background='green',
        foreground='blue',
        highlightthickness='20',
        relief = 'groove',
        font=('Helvetica', 18, 'bold'))
    s.map('TButton',
        foreground=[('disabled', 'yellow'),
                    ('pressed', 'red'),
                    ('active', 'blue')],
        background=[('disabled', 'magenta'),
                    ('pressed', '!focus', 'cyan'),
                    ('active', 'green')],
        highlightcolor=[('focus', 'green'),
                        ('!focus', 'red')])

    # txt.focus()
    

    combo = ttk.Combobox(tab1)
    combo['values']=(1,2,3,4,5,"Six")
    combo.grid(row=2,column=1)
    
    chk_state = tk.BooleanVar()
    chk_state.set(True)
    chk = ttk.Checkbutton(tab1,text="choose",var=chk_state)
    chk.grid(column=0,row=2)

    
    rad1 = ttk.Radiobutton(tab1, text="First", value=1, variable=selected)
    rad2 = ttk.Radiobutton(tab1, text="Second", value=2, variable=selected)
    rad3 = ttk.Radiobutton(tab1, text="Third", value=3, variable=selected)

    rad1.grid(row=3,column=0)
    rad2.grid(row=3,column=1)
    rad3.grid(row=3,column=2)

    
    tab1.mainloop()


if __name__ == "__main__":
    main()
    