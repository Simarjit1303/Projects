# importing library
import time
from tkinter import *
from Login_Page import Main
from PIL import ImageTk, Image

w = Tk()

width_of_window = 427
height_of_window = 250
screen_width = w.winfo_screenwidth()
screen_height = w.winfo_screenheight()
x_coordinate = (screen_width / 2) - (width_of_window / 2)
y_coordinate = (screen_height / 2) - (height_of_window / 2)
w.geometry("%dx%d+%d+%d" % (width_of_window, height_of_window, x_coordinate, y_coordinate))
# w.configure(bg='#ED1B76')
w.overrideredirect(1)


# new window to open
def new_win():
    Main(Tk())
    mainloop()


Frame(w, width=427, height=250, bg='#272727').place(x=0, y=0)
label1 = Label(w, text='PROGRAMMED', fg='white', bg='#272727')  # decorate it
label1.configure(font=("Helvetica", 24, "bold"))
label1.place(x=80, y=90)

label2 = Label(w, text='Loading...', fg='white', bg='#272727')  # decorate it
label2.configure(font=("Calibri", 11))
label2.place(x=10, y=215)

# making animation

image_a = ImageTk.PhotoImage(Image.open('../Face_Recognition_Attendence_System/images/c2.png'))
image_b = ImageTk.PhotoImage(Image.open('../Face_Recognition_Attendence_System/images/c1.png'))

for i in range(5):  # 5loops
    Label(w, image=image_a, border=0, relief=SUNKEN).place(x=180, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=200, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=220, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=180, y=145)
    Label(w, image=image_a, border=0, relief=SUNKEN).place(x=200, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=220, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=180, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=200, y=145)
    Label(w, image=image_a, border=0, relief=SUNKEN).place(x=220, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=180, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=200, y=145)
    Label(w, image=image_b, border=0, relief=SUNKEN).place(x=220, y=145)
    Label(w, image=image_a, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

w.destroy()
new_win()
w.mainloop()
