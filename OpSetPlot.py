from Tkinter import *

from PlotUtils import *


class OpSetPlot(Frame):
    spect_w = None
    axial_w = None

    def __init__(self, master, files, plot_area):
        Frame.__init__(self, master)

        self.files = files
        self.plot_area = plot_area
        self.spectra = BooleanVar()
        self.spectra.set(False)
        self.current_plane = 1

        top_frame = Frame(self)
        top_frame.pack(expand=1, fill=BOTH)

        bottom_frame = Frame(self)
        bottom_frame.pack(expand=1, fill=BOTH)

        plotctrl_frame = Frame(bottom_frame)
        plotctrl_frame.pack(side=TOP)

        slider_frame = Frame(bottom_frame)
        slider_frame.pack(side=TOP, expand=1, fill=BOTH)

        scale_frame = Frame(bottom_frame)
        scale_frame.pack(side=TOP, expand=1, fill=BOTH)

        # File Tree
        Label(top_frame, text="File/Dataset:").pack(anchor=W)

        self.file_tree = DataTree(top_frame)
        self.file_tree.pack(anchor=E, fill=BOTH, expand=1)
        self.file_tree.tree.bind("<Double-Button-1>", self.plot)
        self.file_tree.tree.bind("<Return>", self.plot)

        self.plot_set = Button(plotctrl_frame, text="Plot Dataset",
                               command=self.plot)
        self.plot_set.pack(side=LEFT)

        # Spectrum plotting stuff
        self.pick_mode = StringVar()
        self.pick_mode.set('value')

        Radiobutton(plotctrl_frame, text="Value", variable=self.pick_mode,
                    value='value').pack(anchor=W)
        Radiobutton(plotctrl_frame, text="Spectra", variable=self.pick_mode,
                    value='spectra').pack(anchor=W)
        Radiobutton(plotctrl_frame, text="Axial", variable=self.pick_mode,
                    value='axial').pack(anchor=W)

        # Axial Slider
        Label(slider_frame, text="Axial plane:").pack(anchor=W)
        self.axial = AxialSlider(slider_frame, command=self.update_plot)
        self.axial.pack(side=BOTTOM, expand=1, fill=BOTH)
        # Scale selector
        Label(scale_frame, text="Color Scale:").pack(anchor=W)
        self.scale_mode = StringVar()
        self.scale_mode.set('active')
        self.scale_plane = StringVar()
        Radiobutton(scale_frame, text="Active Plane", variable=self.scale_mode,
                    value='active', command=self.change_scale_mode).pack(anchor=W)
        Radiobutton(scale_frame, text="Global", variable=self.scale_mode,
                    value='global', command=self.change_scale_mode).pack(anchor=W)
        Radiobutton(scale_frame, text="Manual", variable=self.scale_mode,
                    value='manual', command=self.change_scale_mode).pack(anchor=W)
        self.scale_min = StringVar()
        self.scale_min.set('0.0')
        self.scale_max = StringVar()
        self.scale_max.set('1.0')
        self.scale_min_entry = LabeledEntry(scale_frame, text="Min:", width=10,
                                            textvariable=self.scale_min)
        self.scale_min_entry.pack(side=LEFT)
        self.scale_min_entry.disable()
        self.scale_max_entry = LabeledEntry(scale_frame, text="Max:", width=10,
                                            textvariable=self.scale_max)
        self.scale_max_entry.pack(side=LEFT)
        self.scale_max_entry.disable()

        # Label for displaying scalar data
        self.scalarVar = StringVar()
        Label(bottom_frame, textvariable=self.scalarVar).pack(anchor=W)

        # Register plot with callback
        self.cid = self.plot_area.canvas.mpl_connect('button_press_event',
                                                     self.pick)

    # This is the plot pick function, which gets bound to click events on
    # the plot area.
    def pick(self, event):
        if not event.dblclick:
            return
        if self.pick_mode.get() == 'spectra':
            self.add_spectrum(event)
        elif self.pick_mode.get() == 'value':
            x = int(event.xdata)
            y = int(event.ydata)
            item = self.file_tree.tree.selection()[0]
            info = self.file_tree.tree.item(item)
            file_id = info['values'][0]
            set_path = info['values'][1]

            data = self.files[file_id].get_data_2d(set_path, self.current_plane)
            print x, y, data[y, x]
        elif self.pick_mode.get() == 'axial':
            self.add_axial(event)

    def add_spectrum(self, event):
        # Get energy values
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]
        try:
            erg = self.files[file_id].get_erg()
        except NotImplementedError:
            print 'The data file type apparently does not support spectra.'
            return
        except:
            print 'Failed to get energy bounds. Are they present?'
            return
        erg_w = []
        prev_e = 0.0
        for e in reversed(erg):
            erg_w.append(e-prev_e)
            prev_e = e
        erg_w.reverse()

        # Build array
        set_name = info['values'][1]
        set_pfx = set_name.rsplit('/', 1)[0]

        # get the index of the region that was clicked
        x = int(event.xdata)
        y = int(event.ydata)

        spect = []
        for g in xrange(self.files[file_id].ng):
            g_name = set_pfx + "/" + str(g+1).zfill(3)
            data = self.files[file_id].get_data(g_name)
            spect.append(data[0][y][x]*erg[g]/erg_w[g])

        if self.spect_w is None:
            self.spect_w = Toplevel()
            self.spect_pa = PlotArea(self.spect_w)
            self.spect_pa.pack(fill=BOTH, expand=1)
            # Bind the window destruction protocol to the clear function
            self.spect_w.protocol("WM_DELETE_WINDOW", self.kill_spect)

        self.spect_pa.plot_line(erg, spect, logx=True)

    def add_axial(self, event):
        # Get energy values
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]

        # Build array
        set_name = info['values'][1]

        # get the index of the region that was clicked
        x = int(event.xdata)
        y = int(event.ydata)

        axial = self.files[file_id].get_data(set_name)[:, y, x]

        # Mesh. At some point, derrive this from the actual data
        mesh = numpy.linspace(0.0, 1.0, len(axial))

        if self.axial_w is None:
            self.axial_w = Toplevel()
            self.axial_pa = PlotArea(self.axial_w)
            self.axial_pa.pack(fill=BOTH, expand=1)
            # Bind the window destruction protocol to the clear function
            self.axial_w.protocol("WM_DELETE_WINDOW", self.kill_axial)
        self.axial_pa.plot_line(mesh, axial, xlabel="Normalized Axial Height",
                                ylabel="Scalar Flux")

    def kill_spect(self):
        self.spect_w.destroy()
        self.spect_w = None

    def kill_axial(self):
        self.axial_w.destroy()
        self.axial_w = None

    def change_scale_mode(self):
        if self.scale_mode.get() == 'manual':
            self.scale_min_entry.enable()
            self.scale_max_entry.enable()
        else:
            self.scale_min_entry.disable()
            self.scale_max_entry.disable()
        self.plot()

    def select_file(self, file_id=-1):
        file_id = self.file_list.curselection()[0]
        self.file_id = file_id
        datasets = self.files[file_id].set_names

        self.data_list.delete(0, END)
        for i, dset in enumerate(datasets):
            self.data_list.insert(END, dset)

    def update_plot(self, plane):
        if self.current_plane != self.axial.get():
            self.current_plane = self.axial.get()
            self.plot()

    def plot(self, dummy=-1):
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]

        info = self.files[file_id].get_data_info(set_path)

        if info.ndim == 0:
            # Display scalar data
            data = self.files[file_id].get_data(set_path)
            self.scalarVar.set(set_path[1:] + ': ' + str(data))
        else:
            # Plot 2D data
            self.axial.update(1, info.n_planes)

            data = self.files[file_id].get_data_2d(set_path, self.current_plane)

            min_ = None
            max_ = None

            # If we are doing global data scale, grab the scale bounds from the 3D
            # data before we flatten it. The other options will be taken care of
            # later.
            if self.scale_mode.get() == 'global':
                min_ = info.glb_min
                max_ = info.glb_max
            elif self.scale_mode.get() == 'manual':
                min_ = float(self.scale_min.get())
                max_ = float(self.scale_max.get())

            name = set_path.split('/')[-1]

            self.plot_area.plot(data, name, min_, max_)

    def update(self, files):
        self.files = files
        self.file_tree.update(self.files)
