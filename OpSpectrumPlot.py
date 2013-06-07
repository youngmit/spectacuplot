from Tkinter import *

from PlotUtils import *


class OpSpectrumPlot(Frame):
    def __init__(self, master, files, plot_area, side=TOP):
        Frame.__init__(self, master)

        self.plot_area = plot_area

        self.tree = DataTree(self)
        self.tree.tree.pack(expand=1, fill=BOTH, side=TOP)

        self.plot_button = Button(self, text='Plot Spectrum', command=self.plot)
        self.plot_button.pack(side=TOP)

    def update(self, files):
        self.files = files
        self.tree.update(files)

    def plot(self):
        print "plotting"
