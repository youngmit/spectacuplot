from Tkinter import *

from PlotUtils import *


class OpSetPlot(Frame):
    w = None

    def __init__(self, master, files, plot_area):
        Frame.__init__(self, master)

        self.files = files
        self.plot_area = plot_area
        self.spectra = BooleanVar()
        self.spectra.set(False)
        self.current_plane = 1

        top_frame = Frame(self)
        top_frame.pack()

        bottom_frame = Frame(self)
        bottom_frame.pack(expand=1, fill=BOTH)

        plotctrl_frame = Frame(bottom_frame)
        plotctrl_frame.pack(side=TOP)

        slider_frame = Frame(bottom_frame)
        slider_frame.pack(side=TOP, expand=1, fill=BOTH)

        scale_frame = Frame(bottom_frame)
        scale_frame.pack(side=TOP, expand=1, fill=BOTH)

        # File Tree
        self.file_tree = DataTree(top_frame)
        self.file_tree.tree.pack(fill=BOTH, expand=1)
        self.file_tree.tree.bind("<Double-Button-1>", self.plot)

        self.plot_set = Button(plotctrl_frame, text="Plot Dataset",
                               command=self.plot)
        self.plot_set.pack(side=LEFT)

        # Spectrum plotting stuff
        self.spect_toggle = Checkbutton(plotctrl_frame, text="Plot Spectra",
                                        command=self.toggle_spectra,
                                        variable=self.spectra, onvalue=True,
                                        offvalue=False)
        self.spect_toggle.pack(side=LEFT)

        # Axial Slider
        Label(slider_frame, text="Axial plane:").pack(side=TOP)
        self.axial = AxialSlider(slider_frame, command=self.update_plot)
        self.axial.pack(side=BOTTOM, expand=1, fill=BOTH)

        # Scale selector
        self.scale_mode = StringVar()
        self.scale_mode.set('active')
        self.scale_plane = StringVar()
        Radiobutton(scale_frame, text="Active Plane", variable=self.scale_mode,
                    value='active').pack(anchor=W)
        # Radiobutton(scale_frame, text="This Plane", variable=self.scale_mode,
        #             value='fix').pack(anchor=W)
        Label(scale_frame, textvariable=self.scale_plane)
        Radiobutton(scale_frame, text="Global", variable=self.scale_mode,
                    value='global').pack(anchor=W)

    def toggle_spectra(self):
        if self.spectra.get():
            # Turn off spectra
            self.cid = self.plot_area.canvas.mpl_connect('button_press_event',
                                                         self)
        else:
            # Turn on spectra
            self.plot_area.canvas.mpl_disconnect(self.cid)

    # This is the spectrum plot function, which gets bound to click events on
    # the plot area.
    def __call__(self, event):
        if not event.dblclick:
            return
        if self.w is None:
            self.w = Toplevel()
            self.pa = PlotArea(self.w)
            self.pa.pack(fill=BOTH, expand=1)
            # Bind the window destruction protocol to the clear function
            self.w.protocol("WM_DELETE_WINDOW", self.kill_spect)

        # Get energy values
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]
        erg = self.files[file_id].get_erg()
        erg_w = []
        prev_e = 0.0
        for e in reversed(erg):
            erg_w.append(e-prev_e)
            prev_e = e
        erg_w.reverse()

        # Build array
        set_name = self.plot_area.label.get()
        set_pfx = set_name.split('_')[0]

        # get the index of the region that was clicked
        x = int(event.xdata)
        y = int(event.ydata)

        spect = []
        for g in xrange(self.files[file_id].ng):
            g_name = set_pfx + "_" + str(g+1).zfill(3)
            data = self.files[file_id].get_data(g_name)
            spect.append(data[x][y][0]*erg[g]/erg_w[g])

        self.pa.plot_line(erg, spect, logx=True)

    def kill_spect(self):
        self.w.destroy()
        self.w = None

    def select_file(self, file_id=-1):
        file_id = self.file_list.curselection()[0]
        self.file_id = file_id
        datasets = self.files[file_id].set_names

        self.data_list.delete(0, END)
        for i, dset in enumerate(datasets):
            self.data_list.insert(END, dset)

    def update_plot(self, plane):
        print "update plot"
        if self.current_plane != self.axial.get():
            print 'new plane', plane
            self.plot()

    def plot(self, dummy=-1):
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]

        data = self.files[file_id].get_data(set_path)

        min_ = None
        max_ = None

        # If we are doing global data scale, grab the scale bounds from the 3D
        # data before we flatten it. The other options will be taken care of
        # later.
        if self.scale_mode.get() == 'global':
            min_ = numpy.min(numpy.min(numpy.min(data)))
            max_ = numpy.max(numpy.max(numpy.max(data)))

        if numpy.ndim(data) == 3:
            shape = numpy.shape(data)
            if shape[2] > 1:
                n_axial = shape[0]
                self.axial.update(1, n_axial)
                self.current_plane = self.axial.get()
                data = data[self.current_plane-1, :, :]
            else:
                data = data[:, :, 0]
        name = set_path.split('/')[-1]

        self.plot_area.plot(data, name, min_, max_)

    def update(self, files):
        self.files = files
        self.file_tree.update(self.files)
