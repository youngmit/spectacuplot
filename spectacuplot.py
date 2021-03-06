#!/usr/bin/python2
# import matplotlib
# matplotlib.use('TkAgg')

import sys
import os
import functools

from tkinter import *
from tkinter.ttk import Notebook
from tkinter.filedialog import askopenfilename

from PlotArea import *

from OpDiffPlot import *
from OpSetPlot import *
from OpSpectrumPlot import *



class Spectacuplot(Tk):
    opened_files = []
    img = None
    cbar = None

    def __init__(self):
        Tk.__init__(self)

        pwd = os.path.dirname(__file__)

        # ico = PhotoImage(file=os.path.join(pwd, "icon.png"))
        # self.call('wm', 'iconphoto', self._w, ico)

        self.title("Spectacuplot!")

        left_frame = Frame(self)

        control_frame = Frame(left_frame)
        left_frame.pack(side=LEFT, fill=Y)
        control_frame.pack(anchor=N,fill=BOTH,expand=1)

        # Menu bar
        mb = Menu(self)
        file_menu = Menu(mb)
        file_menu.add_command(label='Open...', command=self.open_dialog,
                              accelerator='Ctrl-O')
        file_menu.add_command(label='Close All Files', command=self.close_files)

        # Get recent files
        self.recent = []
        self.recent_commands = []
        try:
            recent_files = open(os.path.expanduser("~/spectacuplot_recent"), "r")
            for f in recent_files:
                self.recent.append(f.strip())
                self.recent_commands.append(functools.partial(self.open, f.strip()))
            recent_files.close()
        except:
            print("no recent files")

        self.recent_cascade = Menu(file_menu)

        for (f, c) in zip(self.recent, self.recent_commands):
            self.recent_cascade.add_command(label=f, command=c)

        file_menu.add_cascade(label="Recent Files", menu=self.recent_cascade)

        # Set up stuff for quitting Spectacuplot
        file_menu.add_command(label='Exit', command=self.quit)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.bind_all("<Control-o>", self.open_dialog)

        self.config(menu=mb)

        mb.add_cascade(label="File", menu=file_menu)


        # Notebook
        nb = Notebook(control_frame, name="controls")
        nb.enable_traversal()
        nb.pack(expand=1, fill=BOTH)

        # Plot Area
        self.plot_frame = PlotArea(self)
        self.plot_frame.pack(side=LEFT, fill=BOTH, expand=1)

        # This will be used as the notbook tab for plotting individual datasets
        self.plot_set_tab = OpSetPlot(nb, self.opened_files, self.plot_frame)

        # This will be used as the notebook tab for plotting dataset diffs
        self.diff_tab = OpDiffPlot(nb, self.opened_files, self.plot_frame)

        nb.add(self.plot_set_tab, text="Plot Set")
        nb.add(self.diff_tab, text="Diff Sets")

    def quit(self):
        Tk.quit(self)
        self.destroy()

    def open_dialog(self, event=""):
        file_name = askopenfilename()
        self.open(file_name)

    def open_recent(self, value=""):
        self.open(value)

    def open(self, file_name):
        print("opening: ", file_name)
        f = OpenDataFile(file_name)
        self.opened_files.append(f)
        self.plot_set_tab.update(self.opened_files)
        self.diff_tab.update(self.opened_files)
        # apply to recent files list
        if not (file_name in self.recent):
            self.recent.insert(0, file_name)
            c = functools.partial(self.open, file_name)
            self.recent_commands.insert(0, functools.partial(self.open, file_name))
            self.recent_cascade.insert_command(0, label=file_name, command=c)
            if len(self.recent) > 5:
                self.recent.pop()
        # poop out to a file
        recent_files = open(os.path.expanduser("~/spectacuplot_recent"), "w")
        for f in self.recent:
            print(f)
            recent_files.write(f + '\n')
        recent_files.close()


    def close_files(self):
        for f in self.opened_files:
            f.close()
        self.opened_files = []
        self.plot_set_tab.update(self.opened_files)
        self.diff_tab.update(self.opened_files)

    


#app = Spectacuplot()
#
#for i in xrange(1, len(sys.argv)):
#    app.open(sys.argv[i])
#
#
#app.mainloop()
