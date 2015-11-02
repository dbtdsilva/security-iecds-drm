import Tkinter as tk
import tkMessageBox
import os
from playback import Playback

LARGE_FONT= ("Verdana", 12)

class MainWindow(tk.Tk):
  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
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
  def checkCredentials(self, username, password):
    if username == "tania" and password == "abc":
      return True
    else:
      return False
  # ----- ----- ----- ----- ----- ----- ----- ----- --
  def login(self, usernameTextbox, passwordTextbox, controller):
    username = usernameTextbox.get()
    password = passwordTextbox.get()

    if self.checkCredentials(username, password):
      self.l.username = username
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
    passwordLabel.grid(row=4, column=0, pady=5)

    usernameTextbox = tk.Entry(self)
    usernameTextbox.grid(row=1, column=1, columnspan=3, padx=10)
    passwordTextbox = tk.Entry(self)
    passwordTextbox.grid(row=4, column=1, columnspan=3)

    button = tk.Button(self, text="Login!",
    command=lambda: self.login(usernameTextbox, passwordTextbox, controller))
    button.grid(row=6, column=2, pady=10, padx=10)

class List(tk.Frame):
  username = ""
  fileListBox = None
  path = ""

  # ----- Change content for server interaction  -----
  def getFileList(self):    
    self.path = "/run/media/guesswho/188165B769E14099/University/Security/security-iecds-drm/src/player/videos/"
    return os.listdir(self.path)
  # ----- ----- ----- ----- ----- ----- ----- ----- --

  def startPlayback(self):
    if self.fileListBox.curselection()[0] != None:
      playback = Playback(self.path + self.fileListBox.get(self.fileListBox.curselection()[0]))

  def logout(self, controller):
    self.username = ""
    controller.show_frame(Login)

  def listContents(self, label, button1):
    listFiles = self.getFileList()

    button1.grid_remove()
    label.grid_remove()

    labelHint = tk.Label(self, text="Please select the file to open and click 'Open'")
    labelHint.grid(row=1, column=0, columnspan=5, padx=20, pady=15)

    self.fileListBox = tk.Listbox(self, selectmode="single")

    for f in listFiles:
      self.fileListBox.insert("end", f)

    self.fileListBox.grid(row=3, column=1, columnspan=3, rowspan=5, padx=10, pady=10)

    selectBtn = tk.Button(self, text="Play file", command=lambda: self.startPlayback())
    selectBtn.grid(row=8, column=1, padx=10, pady=10)

  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    self.grid_columnconfigure(0, weight=1)

    label = tk.Label(self, text="Login successful!", font=LARGE_FONT)
    label.grid(row=1, column=0, pady=15, padx=20, columnspan=5)

    button1 = tk.Button(self, text="Continue",
    command=lambda: self.listContents(label, button1))
    button1.grid(row=3, column=2, padx=10, pady=10)
    
    logoutBtn = tk.Button(self, text="Logout", command=lambda: self.logout(controller))
    logoutBtn.grid(row=0, column=4, pady=10, padx=10)


app = MainWindow()
app.mainloop()
