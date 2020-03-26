from tkinter import *
from tkinter.ttk import *

def main():
    window = Tk()
    window.title("Hello world!")
    window.geometry('1920x1080')
    
    lbl = Label(window, text="LabelText", font=("Arial Bold", 24))
    lbl.grid(column=0, row=0)
    
    label2 = Label(window, text="", font=("Arial Bold", 24))
    label2.grid(column=0,row=1)

    txt = Entry(window, width=10)
    txt.grid(column=1,row=1)
    
    def clicked():
        lbl.configure(text="You clicked me!?!?")
        label2.configure(text=txt.get())
    btn = Button(window, text="I am a button", bg="orange", fg="blue", command=clicked)
    btn.grid(column=1,row=0)
    
    txt.focus()

    combo = Combobox(window)
    combo.grid(row=2,column=1)

    window.mainloop()


if __name__ == "__main__":
    main()
    