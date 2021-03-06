import tkinter as tk


class ScrolledList(tk.Frame):
    ''' Scrolled list box.  Respsonds to double click.
        Override runCommand
        Bind actions such as button press to handleList
    '''

    def __init__(self, parent, items, **kwargs):
        # Items is an iterable of list box items
        super().__init__(parent)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self.makeWidgets(items, **kwargs)

    def __getattr__(self, name):
        # Delegate unknown methods to the listbox

        return getattr(self.listbox, name)

    def handleList(self, event):
        item = self.listbox.get(tk.ACTIVE)
        self.runCommand(item)

    def makeWidgets(self, items, **kwargs):
        sbar = tk.Scrollbar(self)
        li = tk.Listbox(self, **kwargs)
        li.configure(**kwargs)
        sbar.configure(command=li.yview)
        li.configure(yscrollcommand=sbar.set)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        li.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        li.insert(0, *items)
        li.config(selectmode=tk.SINGLE, setgrid=1)
        li.bind('<Double-1>', self.handleList)
        self.listbox = li

    def runCommand(self, selection):
        # override me
        print(selection)


class ScrolledCanvas(tk.Frame):
    '''
    A canvas with scrollbars.
    It automatically delegates unknown methods to the Canvas widget with __getattr__,
    so we don't have to put in a one-line definition every time we use another method.
    '''

    def __init__(self, master, scrolls, **kwargs):
        tk.Frame.__init__(self, master)
        canv = self.canvas = tk.Canvas(self, **kwargs)
        canv.grid(row=0, column=0, sticky='news')

        if scrolls in (tk.BOTH, tk.VERTICAL):
            ybar = tk.Scrollbar(self, orient=tk.VERTICAL)
            # xlink sbar and canv
            ybar.config(command=canv.yview)
            # move one moves other
            canv.config(yscrollcommand=ybar.set)
            ybar.grid(row=0, column=1, sticky='ns')

        if scrolls in (tk.BOTH, tk.HORIZONTAL):
            xbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
            # xlink sbar and canv
            xbar.config(command=canv.xview)
            # move one moves other
            canv.config(xscrollcommand=xbar.set)
            xbar.grid(row=1, column=0, sticky='ew')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def __getattr__(self, name):
        return getattr(self.canvas, name)

    def setCursor(self, cursor):
        self.canvas.configure(cursor=cursor)
