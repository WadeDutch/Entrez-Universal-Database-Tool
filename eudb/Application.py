import tkinter as tk
import tkinter.ttk as ttk
import api
import config as cfg
import webbrowser
import filesave
from tkinter import filedialog
from globals import endl, sortoptions

class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master=master
        self.pack()

        #runtime settings vars
        self.lastsearch = ""
        self.searchindex = 1
        self.rescount = 0
        #ini settings vars
        try:
            self.initsettings()
        except:
            self.initsettings(True)

        self.create_resultsbox()
        self.create_searchbar()
        self.create_menu()

    def initsettings(self, default=False):
        if (default):
            cfg.resetsettings()
        settings = cfg.loadsettings()
        self.database = tk.StringVar(self, settings["database"])
        self.maxresults = tk.IntVar(self, int(settings["maxresults"]))
        self.links = tk.IntVar(self, settings.getint("links"))
        self.authors = tk.IntVar(self, settings.getint("authors"))
        self.date = tk.IntVar(self, settings.getint("date"))
        self.source = tk.IntVar(self, settings.getint("source"))
        self.title = tk.IntVar(self, settings.getint("title"))
        self.journal = tk.IntVar(self, settings.getint("journal"))
        self.displayorder = list(settings["displayorder"].split(","))
        self.masterdisplayorder = list(settings["masterdisplayorder"].split(","))

    def create_menu(self):
        menubar = tk.Menu(self.master)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label="Change Displayed Info", command= self.opensearchsettings)
        settings.add_command(label="Change Order", command= self.openordersettings)
        settings.add_command(label="Reset Settings", command = lambda: self.initsettings(True))

        save = tk.Menu(menubar, tearoff=0)
        #save.add_command(label="Save Results to Spreadsheet", command= lambda: filesave.saveas(self.lastsearch, self.resultbox.get(1.0, tk.END)))
        save.add_command(label="Save Results As...", command= lambda: filesave.saveas(filedialog.asksaveasfilename(initialdir = "/",title = "Save File",filetypes = (("csv files","*.csv"),("all files","*.*"))), self.resultbox.get(1.0, tk.END)))

        menubar.add_cascade(label="File", menu=save)
        menubar.add_cascade(label="Search Settings", menu=settings)
        self.master.config(menu=menubar)

    def create_searchbar(self):
        #Search entry
        tk.Label(self, text="Search").grid(row=1, column=1, sticky="w")
        self.searchEntry = tk.Entry(self)
        self.searchEntry.grid(row=1, column=2, sticky="w")
        self.searchEntry.bind("<Return>", lambda e: self.search())

        #database entry
        tk.Label(self, text="Database").grid(row=2, column=1, sticky="w")
        self.dbEntry = tk.OptionMenu(self, self.database, *api.getdblist())
        self.dbEntry.grid(row=2, column=2, sticky="ew")

        #sort entry
        '''
        tk.Label(self, text="Sort By").grid(row=2, column=3)
        self.sort = tk.StringVar(self)
        self.sort.set("Default")
        self.sortmenu = tk.OptionMenu(self, self.sort, *sortoptions)
        self.sortmenu.grid(row=2, column = 4, sticky="e")
        '''

        #Page index
        self.indexLabel = tk.StringVar()
        self.indexLabel.set("Showing " + str(self.searchindex) + "-" + str(self.searchindex+self.maxresults.get()-1) + " of 0")
        tk.Label(self.master, textvariable=self.indexLabel).pack()        #(row=1, column=5, sticky="e", columnspan=2)
        self.pageRightBtn = tk.Button(self.master, text="----->")
        self.pageLeftBtn = tk.Button(self.master, text="<-----")
        self.pageRightBtn.bind("<ButtonRelease-1>", lambda e: self.modifyindex(self.maxresults.get()))
        self.pageLeftBtn.bind("<ButtonRelease-1>", lambda e: self.modifyindex(-1*self.maxresults.get()))
        self.pageRightBtn.pack(side="right", fill="x", expand=True, padx = (0,500), pady = (0,25))        #(row=2, column=6)
        self.pageLeftBtn.pack(side = "right", fill="x", expand=True, padx = (500,0), pady = (0,25))       #(row=2, column=5)


        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def create_resultsbox(self):
        self.resultbox = tk.Text(self.master, background="#EFEFEF")
        self.resultbox.pack(fill=tk.BOTH, expand=1, pady=20, padx = 60)
        self.resultbox.config(state=tk.DISABLED)
        self.resultbox.tag_config("link", foreground="blue", underline=1)
        self.resultbox.tag_bind("link","<Button-1>", lambda e: webbrowser.open_new_tab(self.resultbox.get("@%d,%d" % (e.x, e.y)+"linestart+6chars", "@%d,%d" % (e.x, e.y)+"lineend")))
        self.resultbox.bind("<Motion>", self.linkevent)
        self.resultbox.config(cursor="arrow")

    def displayresults(self, results, total):
        #update search indexLabel
        self.indexLabel.set("Showing " + str(self.searchindex) + "-" + str(self.searchindex+self.maxresults.get()-1) + " of " + str(total))
        total = 0
        self.resultbox.config(state=tk.NORMAL)
        self.resultbox.delete(1.0, "end")
        for id in results["uids"]:
            if total >= self.maxresults.get():
                continue
            for dsp in self.displayorder:
                if (getattr(self, dsp).get()):
                    if (dsp == "links"):
                        try:
                            tempstr ="Link: https://www.ncbi.nlm.nih.gov/"+self.database.get()+"/"+id+endl
                        except:
                            tempstr = "Link: Error Generating Link"+endl
                        self.resultbox.insert(tk.INSERT, tempstr, "link")

                    elif (getattr(self, dsp).get()):
                        self.resultbox.insert(tk.INSERT, api.getresultline(results[id], dsp, self.database.get()))

            #end dsp in self.displayorder
            #insert break between results
            self.resultbox.insert(tk.INSERT, "-"*20+endl)
            total += 1
        #disable at end
        self.resultbox.config(state=tk.DISABLED)

    def modifyindex(self, ammount):
        if (self.searchindex + ammount >= 1 and not self.rescount == 0):
            self.searchindex += ammount
            self.search(new=False)
        elif (self.searchindex + ammount < 1 and not self.searchindex == 1):
            self.searchindex = 1
            self.search(new=False)

    def linkevent(self, e):
        if ("link" in self.resultbox.tag_names("@%d,%d" % (e.x, e.y))):
            self.resultbox.config(cursor="hand2")
        else:
            self.resultbox.config(cursor="arrow")

    def search(self, new=True):
        if (new):
            query = self.searchEntry.get()
            try:
                self.WebEnv, self.Key, self.rescount = api.searchdb(query, self.database.get().lower())
            except ValueError:
                self.alert("'"+self.dbEntry.get()+"' is not recognized as a valid Entrez data base, please check spelling or try again later.")
                return None
            self.lastsearch = query
        results = api.getsummary(self.WebEnv, self.Key, start=self.searchindex, count=self.maxresults.get())

        self.displayresults(results, self.rescount)

    def alert(self, msg):
        popup = tk.Tk()
        popup.wm_title("Error")
        tk.Label(popup, text=msg).pack(side="top", fill="x", pady=10)
        tk.Button(popup, text="Okay", command = popup.destroy).pack()
        popup.mainloop()

    def opensearchsettings(self):
        self.top = tk.Toplevel()

        tk.Label(self.top, text="Max Results Displayed").pack()
        tk.Entry(self.top, textvariable = self.maxresults, justify="center").pack()
        for dsp in self.displayorder:
            if (dsp=="links"):
                tk.Checkbutton(self.top, text="Show Links", variable= self.links).pack()
            elif (dsp=="authors"):
                tk.Checkbutton(self.top, text="Show Authors", variable= self.authors).pack()
            elif (dsp=="date"):
                tk.Checkbutton(self.top, text="Show Date", variable= self.date).pack()
            elif (dsp=="source"):
                tk.Checkbutton(self.top, text="Show Source", variable= self.source).pack()
            elif (dsp=="title"):
                tk.Checkbutton(self.top, text="Show Title", variable= self.title).pack()
            elif (dsp=="journal"):
                tk.Checkbutton(self.top, text="Show Journal", variable= self.journal).pack()


        self.top.saveBtn = tk.Button(self.top, text="Save")
        self.top.resetBtn = tk.Button(self.top, text="Reset to Default")
        self.top.saveBtn.pack()
        self.top.resetBtn.pack()
        self.top.saveBtn.bind("<1>", lambda e: cfg.changesettings([("links",self.links.get()),("authors",self.authors.get()),("date",self.date.get()),("source",self.source.get()),("title",self.title.get()),("journal",self.journal.get()),("maxresults",self.maxresults.get())]))
        self.top.saveBtn.bind("<ButtonRelease-1>", lambda e: self.top.destroy())
        self.top.resetBtn.bind("<1>", lambda e: self.initsettings(default=True))
        self.top.resetBtn.bind("<ButtonRelease-1>", lambda e: self.top.destroy())

    def openordersettings(self):
        self.top = tk.Toplevel()
        self.top.comboboxes = []
        for dsp in self.displayorder:
            self.top.comboboxes.append(ttk.Combobox(self.top, values=self.masterdisplayorder, state="readonly")) #switch to tkoption menu
            self.top.comboboxes[-1].pack()
            self.top.comboboxes[-1].set(dsp)
        self.top.save = tk.Button(self.top, text="Save")
        self.top.cancel = tk.Button(self.top, text="Cancel")
        self.top.reset = tk.Button(self.top, text="Reset")
        self.top.save.pack()
        self.top.cancel.pack()
        self.top.reset.pack()
        self.top.save.bind("<1>", lambda e: self.updateorder(self.top.comboboxes))
        self.top.save.bind("<ButtonRelease-1>", lambda e: self.top.destroy())
        self.top.cancel.bind("<ButtonRelease-1>", lambda e: self.top.destroy())
        self.top.reset.bind("<1>", lambda e: self.updateorder(default=True))
        self.top.reset.bind("<ButtonRelease-1>", lambda e: self.top.destroy())


    def updateorder(self, comboboxes="", default=False):
        comma = ","
        if (default):
            self.displayorder=self.masterdisplayorder
            cfg.changesettings([("displayorder",comma.join(self.masterdisplayorder))])
            return
        self.displayorder = [self.masterdisplayorder[cb.current()] for cb in comboboxes]
        cfg.changesettings([("displayorder",comma.join(self.displayorder))])
