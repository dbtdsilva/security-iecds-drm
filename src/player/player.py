import Tkinter as tk
import tkMessageBox
import os
from playback import Playback
from mylist import MyList
import requests
from Crypto.Cipher import AES
import hashlib
import binascii
import json
from PIL import ImageTk, Image
import OpenSSL
from cc_utils import cc_utils


LARGE_FONT = ("Verdana", 12)
PlayerKey = "\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c"
Root_Certificate = "resources/COPY_Security_P3G1_Root.crt"
Local_Certificate = ("resources/COPY_Security_P3G1_Player_1.crt",
                     "resources/COPY_Security_P3G1_Player_1_key.pem")
CC_Certificate = None

path = "." + os.path.sep + "videos" + os.path.sep
modalias = "/sys/devices/virtual/dmi/id/modalias"
logo = "./resources/images/logo.bmp"
icon = "./resources/images/icon.bmp"
cc_cert = None
username = None

player_filelist = ["resources/images/icon.bmp",
                    "resources/images/icon.png",
                    "resources/images/logo.bmp",
                    "resources/COPY_Security_P3G1_Player_1.crt",
                    "resources/COPY_Security_P3G1_Player_1_key.pem",
                    "resources/COPY_Security_P3G1_Root.crt",
                    "__init__.py",
                    "mylist.py",
                    "playback.py",
                    "player.py"]

session = requests.Session()

def fix_encoding(text):
	return ''.join([i if ord(i) < 128 else ' ' for i in text])

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("IEDCS Player")
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.minsize(420, 380)
        self.resizable(width=tk.FALSE, height=tk.FALSE)
        self["bg"] = 'White'

        for F in (Login, List):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        loginFrame = self.frames[Login]
        loginFrame.l = self.frames[List]
        self.show_frame(Login)

        req = session.get("https://localhost/api/valplayer/", verify=Root_Certificate, cert=Local_Certificate)
        if req.status_code != 200:
            if req.status_code == 503:
                tkMessageBox.showwarning("ERROR!", "Server is offline, try again later!")
            else:
                tkMessageBox.showwarning("ERROR!", json.loads(req.content)['message'])
            exit(0)
        salt = req.content
        hash = ""
        for file in player_filelist:
            hash += hashlib.pbkdf2_hmac('sha512', open(file, 'r').read(), salt, 1000)
        hashfiles = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', hash, salt, 1000))
        payload = {"hash": hashfiles}
        req = session.post("https://localhost/api/valplayer/", params=payload, verify=Root_Certificate, cert=Local_Certificate)
        if req.status_code != 200:
            tkMessageBox.showwarning("ERROR!", json.loads(req.content)['message'])
            exit(0)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Login(tk.Frame):
    l = None

    # ----- Change content for server interaction  -----
    def checkCredentials(self, DeviceKey):
        cc = cc_utils()
        (status, cc_cert) = cc.get_cert("CITIZEN AUTHENTICATION CERTIFICATE")
        if status != "Success":
            return (False, status, None)

        req = session.get('https://localhost/api/user/loginchallenge/', verify=Root_Certificate)
        if req.status_code != 200:
            return (False, json.loads(req.content)['message'], None)
        salt = req.content
        signature = cc.sign(salt)

        (ec_aut, cidadao_cn) = cc.get_subca_common_names()
        # cert_pem=cert_pem, sign=sign, cidadao_cn=cidadao_cn, ec_aut=ec_aut, key=dkey
	print fix_encoding(cidadao_cn)
        payload = {"cert_pem": binascii.hexlify(cc_cert),
                   "sign": binascii.hexlify(signature),
                   "cidadao_cn": binascii.hexlify(fix_encoding(cidadao_cn)),
                   "ec_aut": binascii.hexlify(fix_encoding(ec_aut)),
                   "key": binascii.hexlify(DeviceKey)}

        req = session.post("https://localhost/api/user/loginchallenge", json=payload, verify=Root_Certificate)
        if req.status_code == 200:
            obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cc_cert)
            names = obj.get_subject().get_components()
            username = None
            for (name, value) in names:
                if 'CN' == name:
                    username = value
            if username is None:
                return (False, "Your certificate doesn't have CN defined.", None)
            return (True, "Logged in", username)
        else:
            return (False, json.loads(req.content)['message'], None)

    # ----- ----- ----- ----- ----- ----- ----- ----- --

    def login(self, controller):
        # ----- Calculate deviceKey -----------
        f = open(modalias, "r")
        self.l.DeviceKey = hashlib.sha256(f.read()).digest()
        # ---------------------------------------
        
        (valid, message, username) = self.checkCredentials(self.l.DeviceKey)
        if valid:
            self.l.username = username
            # Manage directories
            # -- Check if videos directory exists
            if not os.path.exists(path) or not os.path.isdir(path):
                os.mkdir(path)
            # -- Check if user videos directory exists
            if not os.path.exists(path + binascii.hexlify(username)) or \
                    not os.path.isdir(path + binascii.hexlify(username)):
                os.mkdir(path + binascii.hexlify(username))

            self.l.listContents()
            controller.show_frame(List)
        else:
            tkMessageBox.showwarning("ERROR!", message)


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
        #usernameLabel.grid(row=9, column=0, pady=10, padx=10)
        pinLabel = tk.Label(self, text="Citizen Card Pin: ", font=LARGE_FONT)
        pinLabel["bg"] = 'White'
        pinLabel["fg"] = 'Blue'
        #pinLabel.grid(row=10, column=0, pady=10, padx = 10)

        #usernameTextbox = tk.Entry(self)
        #usernameTextbox.grid(row=9, column=1, columnspan=3)
        pinTextbox = tk.Entry(self, show="*")
        #pinTextbox.grid(row=10, column=1, columnspan=3)

        button = tk.Button(self, text="Login using Portuguese Citizen Card!",
                           command=lambda: self.login(controller))
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
    def startPlayback(self, titleid):
        pos = self.titleids[titleid]

        if titleid == None:
            tkMessageBox.showwarning("Oops!", "No file was selected. Please select the file you want to play.")
            return

        payload = {"title": str(pos["id"]), "seed_only": '1'}
        req = session.get('https://localhost/api/title', params=payload, stream=True,
                          verify=Root_Certificate)
        if req.status_code != 200:
            tkMessageBox.showwarning("Oops!", json.loads(req.content)['message'])
            return
        cryptoHeader = req.raw.read(48)
        seed = cryptoHeader[:32]
        iv = cryptoHeader[32:]
        req.raw.close()

        seed_dev_key = AES.new(self.DeviceKey, AES.MODE_ECB).encrypt(seed)

        payload = {"key": binascii.hexlify(seed_dev_key)}
        #print payload
        req = session.post('https://localhost/api/title/validate/' + str(pos["id"]), json=payload,
                            verify=Root_Certificate)
        if req.status_code != 200:
            tkMessageBox.showwarning("Oops!", json.loads(req.content)['message'])
            return
        seed_dev_user_key = req.content
        print "Player key: ", binascii.hexlify(PlayerKey)
        FileKey = AES.new(PlayerKey, AES.MODE_ECB).encrypt(seed_dev_user_key)
        print "Device key: ", binascii.hexlify(self.DeviceKey)
        print "File key:   ", binascii.hexlify(FileKey)
        print "Seed:       ", binascii.hexlify(seed)

        videofile = path + binascii.hexlify(self.username) + os.path.sep + \
                    binascii.hexlify(pos['title']+' - '+pos['author'])
        stream = None
        if not os.path.exists(videofile):
            stream = session.get('https://localhost/api/title/' + str(pos["id"]), stream=True,
                                 verify=Root_Certificate)
        Playback(videofile, FileKey, iv, stream)
        FileKey = None
        del FileKey

    # ----- ----- ----- ----- ----- ----- ----- ----- --

    def logout(self, controller):
        self.username = ""
        req = session.post('https://localhost/api/user/logout', verify=Root_Certificate)
        self.fileListBox = None
        controller.show_frame(Login)

    def listContents(self):
        req = session.get('https://localhost/api/title/user', verify=Root_Certificate)

        self.titleids = json.loads(req.content)
        
        self.fileListBox = MyList(self, self.titleids)

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

        self.fileListBox = None

        logoutBtn = tk.Button(self, text="Logout", command=lambda: self.logout(controller))
        logoutBtn["bg"] = 'White'
        logoutBtn["fg"] = 'Blue'
        logoutBtn.grid(row=0, column=4, pady=10, padx=10)


app = MainWindow()
app.mainloop()
