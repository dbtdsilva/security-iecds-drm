import Tkinter as tk
import tkMessageBox

# Define functions
def checkCredentials():
  username = usernameTextBox.get()
  password = passwordTextBox.get()

  if username == 'tania' and password == 'abc':
    return True
  else:
    return False


def login():
  print('login clicked: ')
  if checkCredentials():
    window.close()
  else:
   tkMessageBox.showerror('Error', 'Login failed!') 

#----------------------------------------------------------------------
# Main function
if __name__ == "__main__":
  # Create window
  window = tk.Tk()
  window.title('IEDCS')

  # Create widgets
  label = tk.Message(window, text = 'IEDCS Player', width = 200)
  usernameTextBox = tk.Entry(window)
  usernameLabel = tk.Label(window, text='Username: ')
  passwordLabel = tk.Label(window, text='Password: ')
  passwordTextBox = tk.Entry(window)
  loginBtn = tk.Button(window, text = 'Login', command = login)

  label.grid(row = 0, column = 0, columnspan = 3, pady = 10)
  label.config(fg = 'blue')
  usernameLabel.grid(row = 1, column = 0)
  passwordLabel.grid(row = 2, column = 0)
  usernameTextBox.grid(padx = 10, row = 1, column = 1, columnspan = 2)
  passwordTextBox.grid(padx = 10, row = 2, column = 1, columnspan = 2)
  loginBtn.grid(padx = 10, pady = 10, row = 4, column = 1)

  window.mainloop()
