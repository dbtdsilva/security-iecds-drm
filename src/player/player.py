import Tkinter as tk
import tkMessageBox
import os
from playback import Playback
import requests
from Crypto.Cipher import AES
import hashlib
import binascii
import json
from PIL import ImageTk, Image

LARGE_FONT = ("Verdana", 12)
PlayerKey = "\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c"
path = "." + os.path.sep + "videos" + os.path.sep
modalias = "/sys/devices/virtual/dmi/id/modalias"
logo = "./resources/images/logo.bmp"
icon = "./resources/images/icon.bmp"


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("IEDCS Player")
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.minsize(310, 310)
        self["bg"] = 'White'

        for F in (Login, List):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        loginFrame = self.frames[Login]
        loginFrame.l = self.frames[List]
        self.show_frame(Login)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Login(tk.Frame):
    l = None

    # ----- Change content for server interaction  -----
    def checkCredentials(self, username, password, DeviceKey):

        payload = {"username": username, "key": binascii.hexlify(DeviceKey)}
        self.l.session = requests.Session()
        req = self.l.session.post('https://localhost/api/user/login/', json=payload, verify=False)

        if req.status_code == 200:
            return True
        else:
            return False

    # ----- ----- ----- ----- ----- ----- ----- ----- --

    def login(self, usernameTextbox, passwordTextbox, controller):
        username = usernameTextbox.get()
        password = passwordTextbox.get()

        # ----- Calculate deviceKey -----------
        f = open(modalias, "r")
        self.l.DeviceKey = hashlib.sha256(f.read()).digest()
        # ---------------------------------------

        if self.checkCredentials(username, password, self.l.DeviceKey):
            self.l.username = username
            # Manage directories
            # -- Check if videos directory exists
            if not os.path.exists(path) or not os.path.isdir(path):
                os.mkdir(path)
            # -- Check if user videos directory exists
            if not os.path.exists(path + username) or not os.path.isdir(path + username):
                os.mkdir(path + username)

            self.l.fileListBox.delete(0, "end")
            self.l.listContents()
            controller.show_frame(List)
        else:
            tkMessageBox.showwarning("ERROR!", "Login credentials are wrong!")

        usernameTextbox.delete(0, "end")
        passwordTextbox.delete(0, "end")

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self["bg"] = 'White'
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(5, weight=1)
        logoImg = ImageTk.PhotoImage(Image.open(logo))
        panel = tk.Label(self, image=logoImg)
        panel["bg"] = 'White'
        panel.image = logoImg
        panel.grid(row=0, column=0, pady=10, padx=10, columnspan=5, rowspan=5)

        wlabel = tk.Label(self, text="Welcome to the IEDCS Player!", font="Verdana 12 bold")
        wlabel["bg"] = 'White'
        wlabel.grid(row=6, column=0, pady=10, padx=10, columnspan=5, rowspan=2)

        label = tk.Label(self, text="Please login to continue...", font=LARGE_FONT)
        label["bg"] = 'White'
        label["fg"] = 'Blue'
        label.grid(row=8, column=0, pady=10, padx=10, columnspan=5)

        usernameLabel = tk.Label(self, text="Username: ", font=LARGE_FONT)
        usernameLabel["bg"] = 'White'
        usernameLabel["fg"] = 'Blue'
        usernameLabel.grid(row=9, column=0, pady=10, padx=10)
        passwordLabel = tk.Label(self, text="Password: ", font=LARGE_FONT)
        passwordLabel["bg"] = 'White'
        passwordLabel["fg"] = 'Blue'
        # passwordLabel.grid(row=10, column=0, pady=10, padx = 10)

        usernameTextbox = tk.Entry(self)
        usernameTextbox.grid(row=9, column=1, columnspan=3)
        passwordTextbox = tk.Entry(self, show="*")
        # passwordTextbox.grid(row=10, column=1, columnspan=3)

        button = tk.Button(self, text="Login!",
                           command=lambda: self.login(usernameTextbox, passwordTextbox, controller))
        button.grid(row=12, column=1, pady=10, padx=10, columnspan=2)
        button["fg"] = "Blue"
        button["bg"] = "White"


class List(tk.Frame):
    username = ""
    fileListBox = None
    DeviceKey = None
    session = None
    titleids = []

    # ----- Change content for server interaction  -----
    def getFileList(self):
        req = self.session.get('https://localhost/api/title/user', verify=False)

        j = json.loads(req.content)
        l = []
        for a in j:
            l.append(a['title'] + " - " + a['author'])
            self.titleids.append(a)

        return l

    def startPlayback(self):
        cryptoHeader = ''
        FileKey = ''

        title = self.fileListBox.get(self.fileListBox.curselection()[0])
        pos = self.titleids[self.fileListBox.curselection()[0]]

        if title == None:
            tkMessageBox.showwarning("Oops!", "No file was selected. Please select the file you want to play.")
            return
            # Check if file exists
            # -- If the file exists, if it doesn't, download it
        if not os.path.exists(path + self.username + os.path.sep + title):
            handle = open(path + self.username + os.path.sep + title, "w")
            req = self.session.get('https://localhost/api/title/' + str(pos["id"]), verify=False)
            if req.status_code != 200:
                tkMessageBox.showwarning("Oops!", "File download failed.")
                return
            cryptoHeader = req.content[:32]
            handle.write(req.content[32:])
            handle.close()
        else:
            payload = {"title": str(pos["id"]), "seed_only": '1'}
            req = self.session.get('https://localhost/api/title', params=payload, verify=False)
            if req.status_code != 200:
                tkMessageBox.showwarning("Oops!", "Download failed.")
                return
            cryptoHeader = req.content

        print cryptoHeader

        # -- Read file
        # -- Create file key
        seed_dev_key = AES.new(self.DeviceKey, AES.MODE_ECB).encrypt(cryptoHeader)

        payload = {"key": binascii.hexlify(seed_dev_key)}
        req = self.session.post('https://localhost/api/title/validate/' + str(pos["id"]), json=payload, verify=False)
        seed_dev_user_key = req.content
        print "RESPONSE: ", seed_dev_user_key
        print "PLAYER KEY2: ", PlayerKey
        FileKey = AES.new(PlayerKey, AES.MODE_ECB).encrypt(seed_dev_user_key)

        print "file key: ", FileKey
        playback = Playback(path + self.username + os.path.sep + title, FileKey)

    # ----- ----- ----- ----- ----- ----- ----- ----- --

    def logout(self, controller):
        self.username = ""
        req = self.session.post('https://localhost/api/user/logout', verify=False)
        controller.show_frame(Login)

    def listContents(self):
        listFiles = self.getFileList()

        for f in listFiles:
            self.fileListBox.insert("end", f)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self["bg"] = 'White'
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        labelHint = tk.Label(self, text="Please select the file to open and click 'Open'")
        labelHint["bg"] = 'White'
        labelHint["fg"] = 'Blue'
        labelHint.grid(row=1, column=1, columnspan=5, padx=20, pady=15)

        self.fileListBox = tk.Listbox(self, selectmode="single")
        self.fileListBox.grid(row=3, column=1, columnspan=5, rowspan=10)

        selectBtn = tk.Button(self, text="Play file", command=lambda: self.startPlayback())
        selectBtn["bg"] = 'White'
        selectBtn["fg"] = 'Blue'
        selectBtn.grid(row=13, column=1, padx=10, pady=10)

        logoutBtn = tk.Button(self, text="Logout", command=lambda: self.logout(controller))
        logoutBtn["bg"] = 'White'
        logoutBtn["fg"] = 'Blue'
        logoutBtn.grid(row=0, column=4, pady=10, padx=10)


app = MainWindow()
app.mainloop()
