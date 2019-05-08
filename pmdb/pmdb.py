import tkinter as tk
from Application import Application


master = tk.Tk()
master.state("zoomed")
master.title("PMDB")
frame = Application(master)
master.mainloop()
