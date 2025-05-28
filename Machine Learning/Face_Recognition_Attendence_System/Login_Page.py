from tkinter import *
from tkinter import messagebox
from attendence import Attendance
from PIL import Image, ImageTk, ImageDraw
from math import *
from datetime import *


class Main:
    def __init__(self, root):
        self.password_text = None
        self.username_text = None
        self.username = None
        self.frame = None
        self.heading = None
        self.code = None
        self.new_login_button = None
        self.img_label = None
        self.img = None
        self.login_frame = None
        self.login_button = None
        self.register_button = None
        self.password_entry = None
        self.new_employee = None
        self.img = None
        self.origin = None
        self.clock = None
        self.draw = None
        self.bg = None
        self.h = None
        self.m = None
        self.s = None
        self.hr = None
        self.min_ = None
        self.sec_ = None

        self.root = root
        self.root.geometry('400x550+0+0')
        self.root.title("WELCOME")
        self.root.config(bg="#021e2f")
        self.root.resizable(bool(0), bool(0))
        self.root.focus()

        self.new_img = Image.new("RGB", (400, 400), (2, 30, 47))
        self.lbl_img = Image.open('../Face_Recognition_Attendence_System/images/faces.jpg')
        self.lbl_img = self.lbl_img.resize((300, 300), Image.Resampling.LANCZOS)
        self.new_img.paste(self.lbl_img, (50, 50))
        self.new_img.save('../Face_Recognition_Attendence_System/images/new_img.png')

        self.wlc_lbl = Label(self.root, text="\nFace Recognition\n Attendance System", font=("Book Antigua", 20, 'bold'),
                             fg="white", compound=BOTTOM, bg="#081923", bd=0)
        self.wlc_lbl.place(x=20, y=50, height=450, width=350)
        self.wlc_img = ImageTk.PhotoImage(file="../Face_Recognition_Attendence_System/images/new_img.png")
        self.wlc_lbl.config(image=self.wlc_img)

        #        Buttons
        self.employee = Button(self.root, text='Employee', font=('Times New Roman', 15), bg='ghostwhite', width=10
                               , command=self.employee)
        self.employee.place(x=20, y=500, width=180)
        self.admin = Button(self.root, text='Admin', font=('Times New Roman', 15), bg='ghostwhite', width=10,
                            command=self.admin)
        self.admin.place(x=200, y=500, width=171)

        # self.copyWrite = Text(self.root, foreground='khaki', background=self.root.cget("background"), borderwidth=0)
        # self.copyWrite.tag_configure("superscript", offset=4)
        # self.copyWrite.insert("insert", "Developed by SIMAR")
        # self.copyWrite.configure(state="disabled")
        # self.copyWrite.pack(side="top")
        # self.copyWrite.place(x=570, y=300)


    def employee(self):
        self.new_employee = Toplevel()
        self.new_employee.focus()
        Attendance(self.new_employee)

    def admin(self):
        def login():
            def search():
                self.f = open("../Face_Recognition_Attendence_System/venv/att.csv", "r")
                c = 0
                b = []
                for i in range(1, 31):
                    b.append("Absent")

                for line in self.f:
                    self.x = line.split(" ")
                    if self.x[0] == self.id_entry.get():
                        self.l1 = Label(self.report, text=self.x[0] + " " + self.x[1] + " " + self.x[2] + " ",
                                        bg="#081923", fg='ghostwhite')
                        m = self.x[2].split("-")
                        for i in range(0, 30):
                            if i == int(m[2]):
                                b[i] = "Pres"
                        self.l1.grid(row=c + 2, column=0)
                        c += 1
                c1 = 0
                c2 = 0
                self.t = Toplevel()
                for i in range(1, 30):
                    if b[i] == "Absent":
                        c1 = c1 + 1
                        self.l = Label(self.t, text=str(i) + " " + str(b[i]) + " ", fg="red")
                    else:
                        c2 = c2 + 1
                        self.l = Label(self.t, text=str(i) + " " + str(b[i]) + " ", fg="blue")

                    self.l.grid(row=i, column=0)
                # print(c1, c2)

            if self.username.get() == 'Admin' and self.password_entry.get() == 'Root':
                self.login_frame.focus()
                self.report = Toplevel()
                self.report.focus()
                self.report.config(bg="#081923")
                self.report.resizable(0, 0)

                self.id_label = Label(self.report, text="ID", width=10, bg="#081923", fg='ghostwhite')
                self.id_label.grid(row=0, column=0)
                self.id_entry = Entry(self.report)
                self.id_entry.focus()
                self.id_entry.grid(row=0, column=1)
                self.go_button = Button(self.report, text="Go", width=10, command=search, bg='ghostwhite')
                self.go_button.grid(row=0, column=2)
                self.login_frame.destroy()

            elif self.username.get() != 'Admin' and self.password_entry.get() != 'Root':
                messagebox.showerror("invalid", "invalid username and password")
            elif self.password_entry.get() != 'Root':
                messagebox.showerror("invalid", "invalid  password")
            elif self.username.get() != "Admin":
                messagebox.showerror("invalid", "invalid username ")

        def clock_image(hr, min_, sec_):
            self.clock = Image.new("RGB", (400, 400), (8, 25, 35))
            self.draw = ImageDraw.Draw(self.clock)
            # =====For Clock Image
            self.bg = Image.open("../Face_Recognition_Attendence_System/images/c.png")
            self.bg = self.bg.resize((300, 300), Image.Resampling.LANCZOS)
            self.clock.paste(self.bg, (50, 50))

            self.origin = 200, 200
            # ====Hour Line Image====
            self.draw.line((self.origin, 200 + 50 * sin(radians(hr)), 200 - 50 * cos(radians(hr))), fill="#DF005E",
                           width=4)
            # ====Min Line Image====
            self.draw.line((self.origin, 200 + 80 * sin(radians(min_)), 200 - 80 * cos(radians(min_))), fill="white",
                           width=3)
            # ====Sec Line Image====
            self.draw.line((self.origin, 200 + 80 * sin(radians(sec_)), 200 - 100 * cos(radians(sec_))), fill="yellow",
                           width=2)
            self.draw.ellipse((195, 195, 210, 210), fill="#1AD5D5")
            self.clock.save("clock.png")

        def working():
            self.h = datetime.now().time().hour
            self.m = datetime.now().time().minute
            self.s = datetime.now().time().second
            self.hr = (self.h / 12) * 360
            self.min_ = (self.m / 60) * 360
            self.sec_ = (self.s / 60) * 360
            clock_image(self.hr, self.min_, self.sec_)
            self.img = ImageTk.PhotoImage(file="clock.png")
            self.clock_label.config(image=self.img)
            self.clock_label.after(200, working)

        self.login_frame = Toplevel()
        self.login_frame.title("Login")
        self.login_frame.geometry("1350x700+0+0")
        self.login_frame.config(bg="#021e2f")
        self.login_frame.resizable(bool(0), bool(0))

        # ===Background Colors===================
        self.left_label = Label(self.login_frame, bg="#08A3D2", bd=0)
        self.left_label.place(x=0, y=0, relheight=1, width=600)

        self.right_label = Label(self.login_frame, bg="#031F3C", bd=0)
        self.right_label.place(x=600, y=0, relheight=1, relwidth=1)

        # ===Frames==================
        self.login_frame_1 = Frame(self.login_frame, bg="white")
        self.login_frame_1.place(x=250, y=100, width=800, height=500)

        self.title = Label(self.login_frame_1, text="LOGIN HERE", font=("times new roman", 30, "bold"), bg="white",
                           fg="#08A3D2")
        self.title.place(x=250, y=50)

        self.username_text = Label(self.login_frame_1, text="USERNAME", bg="white", fg="grey",
                                   font=("times new roman", 18, "bold"))
        self.username_text.place(x=250, y=150)
        
        self.username = Entry(self.login_frame_1, font=("times new roman", 15), bg="lightgrey")
        self.username.place(x=250, y=180, width=350, height=35)
        self.username.focus()

        self.password_text = Label(self.login_frame_1, text="PASSWORD",  bg="white", fg="grey",
                                   font=("times new roman", 18, "bold"))
        self.password_text.place(x=250, y=250)

        self.password_entry = Entry(self.login_frame_1, font=("times new roman", 15), bg="lightgrey", show="*")
        self.password_entry.place(x=250, y=280, width=350, height=35)

        self.new_login_button = Button(self.login_frame_1, text="Login", font=("times new roman", 20, 'bold'),
                                       fg="white", bg="#800857", command=login)
        self.new_login_button.place(x=250, y=360, width=180, height=40)

        # ===Clock===================
        self.clock_label = Label(self.login_frame, text="\nClock", font=("Book Antigua", 25, 'bold'), fg="white",
                                 compound=BOTTOM, bg="#081923", bd=0)
        self.clock_label.place(x=90, y=120, height=450, width=350)

        working()

        self.copyWrite = Text(self.login_frame_1, foreground='#800857', background='white',
                              borderwidth=0)
        self.copyWrite.tag_configure("superscript", offset=4)
        self.copyWrite.insert("insert", "Developed by SIMAR")
        self.copyWrite.configure(state="disabled")
        self.copyWrite.pack(side="top")
        self.copyWrite.place(x=300, y=450)


if __name__ == '__main__':
    Main(Tk())
    mainloop()
