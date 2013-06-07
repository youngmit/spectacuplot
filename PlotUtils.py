from ttk import *
from Tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from DataFile import *


class PlotArea(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.label = StringVar()
        self.label.set("<no plot>")
        Label(self, textvariable=self.label).pack(side=TOP)

        self.cbar = None

        self.f = Figure()
        self.a = self.f.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)

    def plot(self, data, name='No Name'):
        self.label.set(name)
        self.a.clear()
        self.img = self.a.imshow(data[:, :, 0], interpolation="nearest",
                                 origin="lower")
        if(self.cbar is None):
            self.cbar = self.f.colorbar(self.img)
        else:
            self.cbar.update_bruteforce(self.img)

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    def plot_line(self, datax, datay, logx=False, logy=False, clear=False,
                  name='No Name'):
        self.label.set(name)
        if clear:
            self.a.clear()
        if logx:
            self.a.set_xscale('log')
        if logy:
            self.a.set_yscale('log')
        self.line = self.a.plot(datax, datay)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)


class DataTree:
    items = []
    file_id = []
    data_id = []

    def __init__(self, master):
        self.items = []
        self.data = []

        self.tree = Treeview(master)

    def update(self, files):
        self.files = files

        for item in self.items:
            self.tree.delete(item)
        self.data = []

        for (i, datafile) in enumerate(self.files):
            self.items.append(self.tree.insert("", "end", text=datafile.name))

            for (j, set_name) in enumerate(datafile.set_names):
                self.tree.insert(self.items[len(self.items)-1], "end",
                                 text=set_name, values=(i, j))
