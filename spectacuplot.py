#!/usr/bin/python2
import matplotlib
matplotlib.use('TkAgg')

import sys
from Tkinter import *
from tkFileDialog import askopenfilename

from PlotUtils import *

from OpDiffPlot import *
from OpSetPlot import *
from OpSpectrumPlot import *


class App:
    opened_files = []
    img = None
    cbar = None

    def __init__(self, master):
        main_frame = Frame(master)
        main_frame.pack(fill=BOTH, expand=1)

        control_frame = Frame(main_frame)
        control_frame.pack(side=LEFT, fill=Y, expand=1)

        # Menu bar
        self.mb = Menu(main_frame)
        file_menu = Menu(self.mb)
        file_menu.add_command(label='Open...', command=self.open_dialog)
        file_menu.add_command(label='Exit', command=main_frame.quit)

        master.config(menu=self.mb)

        self.mb.add_cascade(label="File", menu=file_menu)

        # Notebook
        nb = Notebook(control_frame, name="controls")
        nb.enable_traversal()
        nb.pack(expand=1, fill=BOTH)

        # Plot Area
        self.plot_frame = PlotArea(main_frame)
        self.plot_frame.pack(side=RIGHT, fill=BOTH, expand=1)

        # Plot Sets
        self.plot_set = OpSetPlot(nb, self.opened_files, self.plot_frame)

        # Diff Frame
        self.diff_frame = OpDiffPlot(nb, self.opened_files, self.plot_frame)

        # Spectrum Frame
        self.spect_frame = OpSpectrumPlot(nb, self.opened_files,
                                          self.plot_frame)

        nb.add(self.plot_set, text="Plot Set")
        nb.add(self.diff_frame, text="Diff Sets")

    def open_dialog(self):
        file_name = askopenfilename()
        self.open(file_name)

    def open(self, file_name):
        f = DataFile(file_name)
        self.opened_files.append(f)
        file_path = file_name.split('/')
        self.plot_set.file_list.insert(END, file_path[len(file_path)-1])
        self.diff_frame.update(self.opened_files)


root = Tk()

app = App(root)

for i in xrange(1, len(sys.argv)):
    app.open(sys.argv[i])

root.mainloop()
