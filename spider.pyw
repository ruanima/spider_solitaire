#!/usr/bin/python3
# spider.pyw

'''
Spider solitaire.  I wrote this because the games I find online have various deficiencies.
Most annoyingly, they dn't leave enough vertical space between the cards so that you
can see the suits.  In most cases, all you can tell is the rank and color.
Also, they use the protocol that when the player completes a suits from King to Ace, it is
automatically taken out of play immediately. The rule is that it remains in play until
the player takes it out.  Often, this can be used to great advantage in organizing other piles.
'''
from model import Model, Stats, SummaryStats
from view import View
import tkinter as tk
from tkinter.messagebox import showerror, showinfo, askokcancel
from datetime import datetime
import sys
import os
from utils import ScrolledList

FMT = '%Y_%m_%d_%H_%M_%S'      # format strings for datetime objects
FMT2 = '%x %X'


with open('data/help.txt') as fp:
    helpText = fp.read()


class FileList(ScrolledList):
    def __init__(self, parent, dataDir, **kwargs):
        super().__init__(parent, [], **kwargs)
        files = (f[:-4] for f in os.listdir(dataDir) if f.endswith('.spi'))
        dates = [datetime.strptime(f, FMT) for f in files]
        dates.sort()
        dates = [d.strftime(FMT2) for d in dates]
        self.listbox.insert(0, *dates)
        self.listbox.see(tk.END)
        self.listbox.selection_set(tk.END)

    def runCommand(self, selection):
        # LoadFileDialog will handle it
        pass


class LoadFileDialog:
    # Modified slightly from SimpleDialog in tkinter/simpledialog.py
    # The kwargs will be passed to the listbox
    def __init__(self, master, dataDir, **kwargs):
        self.root = tk.Toplevel(master)
        self.answer = None         # the file name
        buttons = ('Okay', 'Cancel')
        okay = 0
        cancel = 1
        title = 'Load Game'
        self.root.title(title)
        self.root.iconname(title)
        frame = tk.Frame(self.root)
        frame.pack()
        self.listbox = FileList(frame, dataDir, **kwargs)
        self.listbox.pack(expand=1, fill=tk.BOTH)
        self.cancel = cancel
        self.okay = okay
        for num in range(len(buttons)):
            s = buttons[num]
            b = tk.Button(frame, text=s,
                          command=(lambda self=self, num=num: self.done(num)))
            b.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.root.protocol('WM_DELETE_WINDOW', self.wm_delete_window)
        self._set_transient(master)

    def _set_transient(self, master, relx=0.5, rely=0.3):
        widget = self.root
        widget.withdraw()  # Remain invisible while we figure out the geometry
        widget.transient(master)
        widget.update_idletasks()  # Actualize geometry information
        if master.winfo_ismapped():
            m_width = master.winfo_width()
            m_height = master.winfo_height()
            m_x = master.winfo_rootx()
            m_y = master.winfo_rooty()
        else:
            m_width = master.winfo_screenwidth()
            m_height = master.winfo_screenheight()
            m_x = m_y = 0
        w_width = widget.winfo_reqwidth()
        w_height = widget.winfo_reqheight()
        x = m_x + (m_width - w_width) * relx
        y = m_y + (m_height - w_height) * rely
        if x+w_width > master.winfo_screenwidth():
            x = master.winfo_screenwidth() - w_width
        elif x < 0:
            x = 0
        if y+w_height > master.winfo_screenheight():
            y = master.winfo_screenheight() - w_height
        elif y < 0:
            y = 0
        widget.geometry("+%d+%d" % (x, y))
        widget.deiconify()  # Become visible at the desired location

    def go(self):
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        self.root.destroy()
        return self.answer

    def wm_delete_window(self):
        self.done(self.cancel)

    def done(self, num):
        if num == self.okay:
            item = self.listbox.get(tk.ACTIVE)
            self.answer = datetime.strptime(item, FMT2).strftime(FMT) + '.spi'
        self.root.quit()


class Spider:
    def __init__(self):
        self.model = Model()
        self.view = View(self, self.quit, width=950,
                         height=1000, scrollregion=(0, 0, 950, 3000))
        self.makeHelp()
        self.circular = tk.BooleanVar()
        self.open = tk.BooleanVar()
        self.circular.set(False)
        self.open.set(False)
        self.circular.trace('w', self.optionChanged)
        self.open.trace('w', self.optionChanged)
        self.makeMenu()
        self.view.start()  # start the event loop

    def deal(self):
        model = self.model
        self.saveStats()
        model.deal(self.circular.get(), self.open.get())
        self.view.show()

    def makeHelp(self):
        top = self.helpText = tk.Toplevel()
        top.transient(self.view.root)
        top.protocol("WM_DELETE_WINDOW", top.withdraw)
        top.withdraw()
        top.resizable(False, True)
        top.title("Spider Help")
        f = tk.Frame(top)
        self.helpText.text = text = tk.Text(
            f, height=30, width=80, wrap=tk.WORD)
        text['font'] = ('helevetica', 12, 'normal')
        text['bg'] = '#ffef85'
        text['fg'] = '#8e773f'
        scrollY = tk.Scrollbar(f, orient=tk.VERTICAL, command=text.yview)
        text['yscrollcommand'] = scrollY.set
        text.grid(row=0, column=0, sticky='NS')
        f.rowconfigure(0, weight=1)
        scrollY.grid(row=0, column=1, sticky='NS')
        tk.Button(f, text='Dismiss', command=top.withdraw).grid(
            row=1, column=0)
        f.grid(sticky='NS')
        top.rowconfigure(0, weight=1)
        text.insert(tk.INSERT, helpText)

    def makeMenu(self):
        top = self.view.menu

        game = tk.Menu(top, tearoff=False)
        game.add_command(label='New', command=self.deal)
        game.add_command(label='Save', command=self.save)
        game.add_command(label='Open', command=self.load)
        game.add_command(label='Quit', command=self.quit)
        top.add_cascade(label='Game', menu=game)

        options = tk.Menu(top, tearoff=False)
        options.add_checkbutton(label='Circular', variable=self.circular)
        options.add_checkbutton(label='Open',  variable=self.open)
        top.add_cascade(label='Options', menu=options)

        stats = tk.Menu(top, tearoff=False)
        stats.add_command(label='Display Stats', command=self.showStats)
        stats.add_command(label='Clear Stats', command=self.clearStats)
        top.add_cascade(label='Stats',   menu=stats)

        top.add_command(label='Help', command=self.showHelp)

    def notdone(self):
        showerror('Not implemented', 'Not yet available')

    def save(self):
        model = self.model
        now = datetime.today().strftime(FMT)
        dataDir = os.path.join(os.path.dirname(sys.argv[0]), 'data')
        if not os.path.exists(dataDir):
            os.mkdir(dataDir)
        saveFile = os.path.join(dataDir, now+'.spi')
        model.save(saveFile)

    def load(self):
        dataDir = os.path.join(os.path.dirname(sys.argv[0]), 'data')
        try:
            filename = LoadFileDialog(
                self.view.root, dataDir, bg='lemonChiffon').go()
            if filename:
                self.model.load(os.path.join(dataDir, filename))
                self.view.show()
        except FileNotFoundError:
            showerror('No Files to Open',
                      'Directory\n%s\ndoes not exist' % dataDir)

    def showHelp(self):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')

    def optionChanged(self, *args):
        if self.model.undoStack or self.model.redoStack:
            showinfo("Option Changed", "Changes Will Take Effect Next Game")
        else:
            self.model.reset(self.circular.get(), self.open.get())
            self.model.adjustOpen(self.open.get())
            self.view.show()

    def saveStats(self):
        model = self.model
        if model.stock:             # not all cards dealt means game abandoned
            return
        if model.statsSaved:    # don't save sats for same game twice
            return
        model.statsSaved = True
        stats = model.stats()
        with open(os.path.join(os.path.dirname(sys.argv[0]), 'stats.txt'), 'a') as fout:
            fout.write('%s %s %s %s %s %s\n' % stats)

    def loadStats(self):
        '''
        Returns None if no stats file found, or [] for empty stats file.
        Retuns a list containing summary stats.
        '''
        try:
            with open(os.path.join(os.path.dirname(sys.argv[0]), 'stats.txt')) as fin:
                stats = [Stats(*s.split()) for s in fin.readlines()]
            std = [stat for stat in stats if stat.variant == 'Standard']
            circ = [stat for stat in stats if stat.variant == 'Circular']
            show = [stat for stat in stats if stat.variant == 'Open']
            both = [stat for stat in stats if stat.variant == 'Both']
            stats = []
            for s in (std, circ, show, both):
                if s:
                    stats.append(self.summary(s))
            return stats
        except IOError:
            return None

    def summary(self, stats):
        '''
        Pre: stats is not empty
        '''
        variant = stats[0][0]
        games = len(stats)
        wins = len([s for s in stats if s.win == 'True'])
        moves = sum([int(s.moves) for s in stats]) // games
        up = sum([int(s.up) for s in stats]) // games
        up1 = sum([int(s.up1) for s in stats]) // games
        return SummaryStats(variant, games, wins, moves, up, up1)

    def showStats(self):
        stats = self.loadStats()
        self.view.showStats(stats)

    def clearStats(self):
        if askokcancel("Confirm Clear Stats", "Do you really want to erase all stats to date?"):
            open(os.path.join(os.path.dirname(
                sys.argv[0]), 'stats.txt'), 'w').close()

    def quit(self):
        self.saveStats()
        self.view.root.quit()


if __name__ == "__main__":
    Spider()
