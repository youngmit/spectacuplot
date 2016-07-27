from ttk import *
from Tkinter import *

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot

from DataFile import *
from DataTree import *

import math
import numpy


class PlotArea(Frame):
    def __init__(self, master, axes="lin"):
        Frame.__init__(self, master)

        self.label = StringVar()
        self.label.set("<no plot>")
        Label(self, textvariable=self.label).pack(side=TOP)

        self.cbar = None

        self.plot_frame = Frame(master=self)
        self.inner_frame = Frame(self.plot_frame)
        self.reset(axes)
        self.plot_frame.pack(fill=BOTH, expand=1)

        # Set up things to plot polar stuff
        self.ang_frame = Frame(master=self)
        self.f_ang, self.a_ang = pyplot.subplots(1, 2)
        

        self.canvas_ang = FigureCanvasTkAgg(self.f_ang, master=self.ang_frame)

    # Wipe out whetever is currently in the figure
    def reset(self, axes="lin"):
        self.inner_frame.destroy()
        self.inner_frame = Frame(self.plot_frame)
        self.f = Figure()
        if axes == "lin":
            self.a = self.f.add_subplot(111)
        elif axes == "polar":
            print "polar axes...?"
            self.a = self.f.add_subplot(111, projection="polar")
        # self.a.set_xlabel("X Pin")
        # self.a.set_ylabel("Y Pin")

        self.canvas = FigureCanvasTkAgg(self.f, master=self.inner_frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.inner_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.inner_frame.pack(fill=BOTH, expand=1)

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
        self.plot_frame.pack(fill=BOTH, expand=1)

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

    def set_log(self, logx, logy):
        print logx, logy
        if logx:
            self.a.set_xscale('log')
        else:
            self.a.set_xscale('linear')
        if logy:
            self.a.set_yscale('log')
        else:
            self.a.set_yscale('linear')

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)

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
        self.plot_frame.pack_forget()
        self.canvas_ang.draw()
        self.canvas_ang.get_tk_widget().pack(fill=BOTH, expand=1)
        self.ang_frame.pack(fill=BOTH, expand=1)
