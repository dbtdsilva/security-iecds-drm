import Tkinter as tk
import tkMessageBox
import os
from playback import Playback
import requests
from Crypto.Cipher import AES
import hashlib
import binascii
import json

LARGE_FONT= ("Verdana", 12)
PlayerKey = "\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c"
#PlayerKey = '12345678901234567890123456789012'
path = "." + os.path.sep + "videos" + os.path.sep
modalias="/sys/devices/virtual/dmi/id/modalias"
uid = 0

class MainWindow(tk.Tk):
  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.title("IEDCS Player")
    container = tk.Frame(self)
    
    container.pack(side="top", fill="both", expand = True)

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    self.frames = {}
    self.minsize(310, 310)

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

    payload = {"username":username, "key":binascii.hexlify(DeviceKey)}
    self.l.session = requests.Session()
    req = self.l.session.post('http://localhost:8000/api/user/login/', json = payload)

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
    #---------------------------------------

    if self.checkCredentials(username, password, self.l.DeviceKey):
        self.l.username = username
        #Manage directories
        # -- Check if videos directory exists
        if not os.path.exists(path) or not os.path.isdir(path):
            os.mkdir(path)
        # -- Check if user videos directory exists
        if not os.path.exists(path + username) or not os.path.isdir(path + username):
            os.mkdir(path + username)

        self.l.listContents()
        controller.show_frame(List)
    else:
        tkMessageBox.showwarning("ERROR!", "Login credentials are wrong!" )
      
    usernameTextbox.delete(0, "end")
    passwordTextbox.delete(0, "end")



  def __init__(self, parent, controller):
    tk.Frame.__init__(self,parent)

    label = tk.Label(self, text="Login to continue...", font=LARGE_FONT)
    label.grid(row=0, column=0, pady=10, padx=10, columnspan=5)

    usernameLabel = tk.Label(self, text="Username: ", font=LARGE_FONT)
    usernameLabel.grid(row=1, column=0, pady=5)
    passwordLabel = tk.Label(self, text="Password: ", font=LARGE_FONT)
    #passwordLabel.grid(row=4, column=0, pady=5)

    usernameTextbox = tk.Entry(self)
    usernameTextbox.grid(row=1, column=1, columnspan=3, padx=10)
    passwordTextbox = tk.Entry(self, show="*")
    #passwordTextbox.grid(row=4, column=1, columnspan=3)

    button = tk.Button(self, text="Login!",
    command=lambda: self.login(usernameTextbox, passwordTextbox, controller))
    button.grid(row=6, column=2, pady=10, padx=10)
    

class List(tk.Frame):
  username = ""
  fileListBox = None
  DeviceKey = None
  session = None
  titleids = []

  # ----- Change content for server interaction  -----
  def getFileList(self):   
    req = self.session.get('http://localhost:8000/api/title/user')

    j = json.loads(req.text)
    l = []
    for a in j:
        l.append(a['title'] + " - " + a['author'])
        self.titleids.append(a)

    return l

  def startPlayback(self):
    cryptoHeader = '12345678901234567890123456789012'
    UserKey = '12345678901234567890123456789012'
    print self.DeviceKey

    aes = AES.new(cryptoHeader, AES.MODE_ECB)
    cryptoDevKey = aes.encrypt(self.DeviceKey)
    aes = AES.new(cryptoDevKey, AES.MODE_ECB)
    cryptoDevUserKey = aes.encrypt(UserKey)
    aes = AES.new(cryptoDevKey, AES.MODE_ECB)
    FileKey = aes.encrypt(PlayerKey)
    aes = AES.new(FileKey, AES.MODE_ECB)

    title = self.fileListBox.get(self.fileListBox.curselection()[0])
    pos = self.titleids[self.fileListBox.curselection()[0]]

    if title != None:
        #Check if file exists
        # -- If the file exists, if it doesn't, download it
        if not os.path.exists(path + self.username + os.path.sep + title):
            print "I think file does not exist"
            with open(path + self.username + os.path.sep + title, "w") as handle:
                print pos["id"]
                req = self.session.get('http://localhost:8000/api/title/' + str(pos["id"]), stream = True)
                if req.status_code != 200:
                    tkMessageBox.showwarning("Oops!", "Download failed." )
                else:
                    print "Downing file"
                    for block in req.iter_request(1024):
                        handle.write(block)
                        print block
        # -- Read file
        #playback = Playback(path + self.username + os.path.sep + title, FileKey)
    else:
        tkMessageBox.showwarning("Oops!", "No file was selected. Please select the file you want to play." )

  # ----- ----- ----- ----- ----- ----- ----- ----- --

  def logout(self, controller):
    self.username = ""
    controller.show_frame(Login)

  def listContents(self):
    listFiles = self.getFileList()
    
    for f in listFiles:
      self.fileListBox.insert("end", f)

  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    self.grid_columnconfigure(0, weight=1)

    labelHint = tk.Label(self, text="Please select the file to open and click 'Open'")
    labelHint.grid(row=1, column=1, columnspan=5, padx=20, pady=15)

    self.fileListBox = tk.Listbox(self, selectmode="single")
    self.fileListBox.grid(row=3, column=1, columnspan=5, rowspan=10)

    selectBtn = tk.Button(self, text="Play file", command=lambda: self.startPlayback())
    selectBtn.grid(row=13, column=1, padx=10, pady=10)

    logoutBtn = tk.Button(self, text="Logout", command=lambda: self.logout(controller))
    logoutBtn.grid(row=0, column=4, pady=10, padx=10)


app = MainWindow()
app.mainloop()
