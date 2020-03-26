# from tkinter import *
# from tkinter.ttk import *
import tkinter as tk
from tkinter import ttk

def main():
    window = tk.Tk()
    window.title("Hello world!")
    window.geometry('1920x1080')
    
    lbl = tk.Label(window, text="LabelText", font=("Arial Bold", 24))
    lbl.grid(column=0, row=0)
    
    label2 = tk.Label(window, text="", font=("Arial Bold", 24))
    label2.grid(column=0,row=1)

    txt = tk.Entry(window, width=10)
    txt.grid(column=1,row=1)
    
    def clicked():
        lbl.configure(text="You clicked me!?!?")
        label2.configure(text=txt.get())
    btn = ttk.Button(window, text="I am a button", command=clicked)#, highlightbackground='#3E4149')
    # btn2 = ttk.Button(window, text="Button2", highlightbackground="red")
    btn.grid(column=1,row=0)
    
    txt.focus()

    combo = ttk.Combobox(window)
    combo.grid(row=2,column=1)

    window.mainloop()


if __name__ == "__main__":
    main()
    