from ttk import *
from Tkinter import *

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot

from DataFile import *

import math
import numpy


class PlotArea(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.label = StringVar()
        self.label.set("<no plot>")
        Label(self, textvariable=self.label).pack(side=TOP)

        self.cbar = None

        self.pin_frame = Frame(master=self)
        self.f = Figure()
        self.a = self.f.add_subplot(111)
        # self.a.set_xlabel("X Pin")
        # self.a.set_ylabel("Y Pin")

        self.canvas = FigureCanvasTkAgg(self.f, master=self.pin_frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.pin_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.pin_frame.pack(fill=BOTH, expand=1)

        # Set up things to plot polar stuff
        self.ang_frame = Frame(master=self)
        self.f_ang, self.a_ang = pyplot.subplots(1, 2)
        

        self.canvas_ang = FigureCanvasTkAgg(self.f_ang, master=self.ang_frame)

    def plot(self, data, name='No Name', min_=None, max_=None, label=None,
             xlabel="X Pin", ylabel="Y Pin"):
        self.label.set(name)
        self.a.clear()
        if data.ndim == 3:
            self.img = self.a.imshow(data[:, :, 0], interpolation="nearest",
                                     origin="upper", vmin=min_, vmax=max_)
        else:
            self.img = self.a.imshow(data[:, :], interpolation="none",
                                     origin="upper", vmin=min_, vmax=max_)
        if(self.cbar is None):
            self.cbar = self.f.colorbar(self.img)
        else:
            self.cbar.update_bruteforce(self.img)

        if not label is None:
            self.cbar.set_label(label)

        self.a.set_xlabel(xlabel)
        self.a.set_ylabel(ylabel)

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        self.ang_frame.pack_forget()
        self.pin_frame.pack(fill=BOTH, expand=1)

    def plot_line(self, datax, datay, logx=False, logy=False, clear=False,
                  name='No Name', label=None, marker=None, xlabel="X",
                  ylabel="Y"):
        self.label.set(name)
        if clear:
            self.a.clear()
        if logx:
            self.a.set_xscale('log')
        if logy:
            self.a.set_yscale('log')
        self.line = self.a.plot(datax, datay, marker=marker, label=label)
        self.a.legend()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)

        self.a.set_xlabel(xlabel)
        self.a.set_ylabel(ylabel)

    def plot_angle(self, data):
        print data
        azi_x = math.cos(data[0])
        azi_y = math.sin(data[0])
        pol_x = 1.0*numpy.sign(azi_x)
        pol_y = math.sin(data[1])*numpy.sign(azi_y)

        for ax in self.a_ang:
            ax.cla()
            ax.set_xlim(left  = -1.0, right = 1.0)
            ax.set_ylim(bottom= -1.0, top   = 1.0)
            ax.set_aspect("equal")

        self.a_ang[0].plot([0, azi_x], [0, azi_y])
        self.a_ang[1].plot([0, pol_x], [0, pol_y])
        self.pin_frame.pack_forget()
        self.canvas_ang.draw()
        self.canvas_ang.get_tk_widget().pack(fill=BOTH, expand=1)
        self.ang_frame.pack(fill=BOTH, expand=1)

class DataTree(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg="black")
        scroll = Scrollbar(self)

        self.tree = Treeview(self, yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)

        self.items = []

        self.tree.pack(side=LEFT, fill=BOTH, expand=1)
        scroll.pack(side=LEFT, fill=Y)

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

        if to > 1:
            self.enable()
        else:
            self.disable()

    def get(self):
        return self.slider.get()

    def enable(self):
        self.slider.config(state=NORMAL, fg='#000', sliderrelief=RAISED)

    def disable(self):
        self.slider.config(state=DISABLED, fg='#888', sliderrelief=FLAT)


class LabeledEntry(Frame):
    def __init__(self, master, textvariable=None, text='', width=None,
                 disabled=False):
        Frame.__init__(self, master)

        self.disabled = False

        self.label = Label(self, text=text)
        self.label.pack(side=LEFT)

        self.entry = Entry(self, textvariable=textvariable, width=width)
        self.entry.pack(side=LEFT)

        if disabled:
            self.disable()

    def enable(self):
        self.disabled = False
        self.entry.config(state=NORMAL, fg='#000')
        self.label.config(fg='#000')

    def disable(self):
        self.disabled = True
        self.entry.config(state=DISABLED, fg='#888')
        self.label.config(fg='#888')


class Error(Exception):
    pass
