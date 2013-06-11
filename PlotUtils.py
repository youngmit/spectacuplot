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

    def plot(self, data, name='No Name', min_=None, max_=None):
        self.label.set(name)
        self.a.clear()
        if data.ndim == 3:
            self.img = self.a.imshow(data[:, :, 0], interpolation="nearest",
                                     origin="lower", vmin=min_, vmax=max_)
        else:
            self.img = self.a.imshow(data[:, :], interpolation="nearest",
                                     origin="lower", vmin=min_, vmax=max_)
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
    def __init__(self, master):
        self.tree = Treeview(master)
        self.items = []

    def update(self, files):
        self.files = files

        # reversing, since removing a node with children removes the children as
        # well. there might be a cleaner way to do this by clearing each of the
        # file nodes, but that might add more burden to the garbage collector
        # down the line.
        for item in reversed(self.items):
            self.tree.delete(item)

        self.items = []

        for (i, datafile) in enumerate(self.files):
            self.add_file(datafile, i)

    def add_file(self, f, f_id):
        file_id = self.tree.insert("", "end", text=f.name)
        self.items.append(file_id)

        self.add_node(file_id, f.data, f_id)

    def add_node(self, p, node, f_id):
        if node.name != '':
            node_id = self.tree.insert(p, "end", text=node.name,
                                       values=(f_id, node.path))
            self.items.append(node_id)
        else:
            node_id = p

        if node.is_grp:
            for child in node.children:
                self.add_node(node_id, child, f_id)


class AxialSlider(Frame):
    def __init__(self, master, command=None):
        Frame.__init__(self, master)

        self.slider = Scale(self, from_=1, to=1, orient=HORIZONTAL,
                            command=command)
        self.disable()

        self.slider.pack(expand=1, fill=BOTH)

    def update(self, from_, to):
        self.slider.config(from_=from_, to=to, state=NORMAL)
        self.enable()

    def get(self):
        return self.slider.get()

    def enable(self):
        self.slider.config(state=NORMAL, fg='#000', sliderrelief=RAISED)

    def disable(self):
        self.slider.config(state=DISABLED, fg='#888', sliderrelief=FLAT)


class Error(Exception):
    pass
