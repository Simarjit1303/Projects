import datetime
import time
import tkinter as tk
import cv2
import numpy as np
import os
import pandas as pd
from PIL import Image



class Attendance:
    def __init__(self, root):
        self.imageNp = None
        self.pilImage = None
        self.Ids = None
        self.faces = None
        self.TrainingImagePath = None
        self.imagePaths = None
        self.detector = None
        self.harcascadePath = None
        self.recognizer = None
        self.face = None
        self.count = None
        self.cap = None
        self.res = None
        self.Id = None
        self.data = 0

        self.window = root
        self.window.title("Attendance System")
        self.window.geometry('350x180')
        # self.window.config(bg='#081923')

        self.lbl1 = tk.Label(self.window, text="Enter ID", width=10)
        self.lbl1.place(x=80, y=5)

        self.lbl2 = tk.Label(self.window, text="Enter Name", width=10)
        self.lbl2.place(x=80, y=55)

        self.txt1 = tk.Entry(self.window, width=10)
        self.txt1.place(x=160, y=5)

        self.txt2 = tk.Entry(self.window, width=10)
        self.txt2.place(x=160, y=55)

        self.message = tk.Label(self.window, text="")
        self.message.place(x=160, y=79)

        self.clearButton1 = tk.Button(self.window, text="Clear", command=self.clear)
        self.clearButton1.place(x=230, y=5)

        self.clearButton2 = tk.Button(self.window, text="Clear", command=self.clear)
        self.clearButton2.place(x=230, y=55)

        self.takeImg = tk.Button(self.window, text="Take Images", command=self.TakeImages)
        self.takeImg.place(x=20, y=105)

        self.trainImg = tk.Button(self.window, text="Train Images", command=self.TrainImages)
        self.trainImg.place(x=110, y=105)

        self.trackImg = tk.Button(self.window, text="Track Images", command=self.TrackImages)
        self.trackImg.place(x=206, y=105)

        self.quitWindow = tk.Button(self.window, text="Quit", command=self.window.destroy)
        self.quitWindow.place(x=300, y=105)

        self.copyWrite = tk.Text(self.window, background=self.window.cget("background"), borderwidth=0)
        self.copyWrite.tag_configure("superscript", offset=4)
        self.copyWrite.insert("insert", "Developed by SIMAR")
        self.copyWrite.configure(state="disabled")
        self.copyWrite.pack(side="top")
        self.copyWrite.place(x=95, y=140)

    def clear(self):
        self.txt1.delete(0, 'end')
        self.txt2.delete(0, 'end')
        self.res = ""
        self.message.configure(text=self.res)

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    def TakeImages(self):
        self.Id = (self.txt1.get())
        if self.is_number(self.Id):
            face_classifier = cv2.CascadeClassifier(
                '../Face_Recognition_Attendence_System/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')

            def face_extractor(img):
                self.cropped_face = None
                self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.faces = face_classifier.detectMultiScale(self.gray, 1.3, 5)

                if self.faces is ():
                    return None

                for (x, y, w, h) in self.faces:
                    self.cropped_face = img[y:y + h, x:x + w]

                return self.cropped_face

            self.cap = cv2.VideoCapture(0)
            self.count = 0

            while True:
                ret, frame = self.cap.read()
                if face_extractor(frame) is not None:
                    self.count += 1
                    self.face = cv2.resize(face_extractor(frame), (500, 500))
                    self.face = cv2.cvtColor(self.face, cv2.COLOR_BGR2GRAY)

                    file_name_path = "../Face_Recognition_Attendence_System/TrainingImage/Train.User." + self.Id + '.' + \
                                     str(self.count) + ".jpg"
                    cv2.imwrite(file_name_path, self.face)

                    cv2.putText(self.face, str(self.count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                    cv2.imshow('Face cropper', self.face)
                    print("FACE FOUND")

                else:
                    print("Face not Found")
                    pass

                if cv2.waitKey(1) == 13 or self.count == 100:
                    break

            self.cap.release()
            cv2.destroyAllWindows()
            print('Collecting Samples Complete!!!')

            res = "Images Saved for " + self.Id
            self.message.configure(text=res)
        else:
            res = "Enter Numeric Id"
            self.message.configure(text=res)

    def TrainImages(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.harcascadePath = \
            "../Face_Recognition_Attendence_System/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"
        self.detector = cv2.CascadeClassifier(self.harcascadePath)
        self.TrainingImagePath = '../Face_Recognition_Attendence_System/TrainingImage'
        self.faces, self.Ids = self.getImagesAndLabels(self.TrainingImagePath)
        self.recognizer.train(self.faces, np.array(self.Ids))
        self.recognizer.write("../Face_Recognition_Attendence_System/TrainingImageLabel/Trainner.yml")
        res = "Image Trained"
        self.message.configure(text=res)

    def getImagesAndLabels(self, path):
        self.imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        print(self.imagePaths)

        self.faces = []

        self.Ids = []

        for imagePath in self.imagePaths:
            self.pilImage = Image.open(imagePath).convert('L')

            self.imageNp = np.array(self.pilImage, 'uint8')

            self.Id = int(os.path.split(imagePath)[-1].split(".")[2])

            self.faces.append(self.imageNp)
            self.Ids.append(self.Id)
        return self.faces, self.Ids

    def TrackImages(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read("../Face_Recognition_Attendence_System/TrainingImageLabel/Trainner.yml")
        self.harcascadePath = \
            "../Face_Recognition_Attendence_System/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(self.harcascadePath)
        self.df = pd.read_csv("../Face_Recognition_Attendence_System/StudentDetails/StudentDetails.csv")
        self.cam = cv2.VideoCapture(0)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.col_names = ['ID', 'Date', 'Time']
        self.attendance = pd.DataFrame(columns=self.col_names)
        while True:
            self.ret, self.im = self.cam.read()
            self.gray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
            self.faces = self.faceCascade.detectMultiScale(self.gray, 1.2, 5)
            for (x, y, w, h) in self.faces:
                cv2.rectangle(self.im, (x, y), (x + w, y + h), (225, 0, 0), 2)
                self.Id, self.conf = self.recognizer.predict(self.gray[y:y + h, x:x + w])
                if self.conf < 50:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    self.attendance.loc[len(self.attendance)] = [self.Id, date, timeStamp]
                    aa = self.df.loc[self.df['ID'] == self.Id]['Name'].values
                    tt = str(self.Id) + "-" + aa[0]
                    print(str(self.Id) + " " + aa[0])

                    count = 0
                    # insert into attendence values(%s,%s,%s)
                    val = (id, aa[0], date)
                else:
                    Id = 'Unknown'
                    tt = str(Id)
                if self.conf > 75:
                    noOfFile = len(os.listdir("../Face_Recognition_Attendence_System/ImagesUnknown")) + 1
                    cv2.imwrite("../Face_Recognition_Attendence_System/ImagesUnknown/Image" + str(noOfFile) + ".jpg",
                                self.im[y:y + h, x:x + w])
                cv2.putText(self.im, str(tt), (x, y + h), self.font, 1, (255, 255, 255), 2)
            self.attendance = self.attendance.drop_duplicates(keep='first', subset=['ID'])
            cv2.imshow('im', self.im)
            # global data
            if cv2.waitKey(1) == ord('q'):
                if self.data == 0:
                    self.data = self.data + 1
                    f = open("../Face_Recognition_Attendence_System/venv/att.csv", "r")
                    self.count=0
                    for line in f:
                        x = line.split(" ")

                        if x[0] == str(self.Id) and str(date)==x[2]:
                            self.count = self.count + 1
                    if self.count == 0:
                        f = open("../Face_Recognition_Attendence_System/venv/att.csv", "a")
                        f.write(str(self.Id) + " " + aa[0] + " " + str(date) + " \n")
                        f.close()
                    print(self.count,x[0] == str(self.Id) , str(date)==x[2])
                else:
                    print("error")
                break

        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        fileName = "../Face_Recognition_Attendence_System/Attendance/Attendance_" + date + ".csv"

        self.attendance.to_csv(fileName, index=False)
        self.cam.release()
        cv2.destroyAllWindows()
        print(self.attendance)
