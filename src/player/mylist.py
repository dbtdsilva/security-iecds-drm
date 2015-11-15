import Tkinter as tk
import tkMessageBox
from PIL import ImageTk, Image
from Tkinter import N, S, W

icon = "./resources/images/icon.png"

class MyList(tk.Frame):

    titleids = []
    parent = None

    def openWindow(self, row):
        title = self.titleids[row]
        self.parent.startPlayback(row)

    def __init__(self, root, titles):
        tk.Frame.__init__(self, root)
        self.titleids = titles
        self.parent = root
        self.canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row = 3, column =7, rowspan = 10, sticky=N+S+W)
        self.canvas.grid(row=3, column=1, columnspan=6, rowspan=10, padx = 10, pady = 10)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.populate()

    def populate(self):
        row = 0
        for title in self.titleids:
            iconImg = ImageTk.PhotoImage(Image.open(icon))
            l = tk.Label(self.frame, image = iconImg, background = "#ffffff")
            l.image = iconImg
            l.grid(row=row, column=0, pady = 5, padx = 5)
            t= title['title'] + '\nBy: ' + title['author'] + '\nCategory: ' + title['category']
            tk.Label(self.frame, text=t, background = "#ffffff").grid(row=row, column=1, columnspan = 3, padx = 5, pady = 5)
            tk.Button(self.frame, text="Play file", command=lambda row=row: self.openWindow(row)).grid(row = row, column = 4)
            row += 1

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root=tk.Tk()
    MyList(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
