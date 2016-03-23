from Tkinter import *

from PlotArea import *

from PlotControls_3D import *

import numpy

class OpSetPlot(Frame):
    spect_w = None
    axial_w = None

    def __init__(self, master, files, plot_area=None):
        Frame.__init__(self, master)

        self.files = files
        self.plot_area = plot_area
        self.spectra = BooleanVar()
        self.spectra.set(False)
        self.current_plane = 1

        # The top frame only holds the file tree
        top_frame = Frame(self)
        top_frame.pack(expand=1, fill=BOTH)

        # File Tree
        Label(top_frame, text="File/Dataset:").pack(anchor=W)

        self.file_tree = DataTree(top_frame)
        self.file_tree.pack(anchor=E, fill=BOTH, expand=1)
        self.file_tree.tree.bind("<Double-Button-1>", self.plot)
        self.file_tree.tree.bind("<Return>", self.plot)

        self.plot_set = Button(top_frame, text="Plot Dataset",
                               command=self.plot)
        self.plot_set.pack(side=LEFT)

        self.controls = PlotControls_3D(self, self.plot_area)
        self.controls.pack(fill=BOTH)

        

        # Label for displaying scalar data
        self.scalarVar = StringVar()
        #Label(bottom_frame, textvariable=self.scalarVar).pack(anchor=W)

        # Register plot with callback
        self.cid = self.plot_area.canvas.mpl_connect('button_press_event',
                                                     self.pick)

    # This is the plot pick function, which gets bound to click events on
    # the plot area.
    def pick(self, event):
        if not event.dblclick:
            return
        if self.controls.pick_mode.get() == 'spectra':
            self.add_spectrum(event)
        elif self.controls.pick_mode.get() == 'value':
            x = int(event.xdata)
            y = int(event.ydata)
            item = self.file_tree.tree.selection()[0]
            info = self.file_tree.tree.item(item)
            file_id = info['values'][0]
            set_path = info['values'][1]

            data = self.files[file_id].get_data_2d(set_path, self.current_plane)
            index = self.nx*self.ny*(self.current_plane-1) + self.nx*y + x+1
            print x, y, self.current_plane, index, data[y, x]
        elif self.controls.pick_mode.get() == 'axial':
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
            spect.append(data[self.current_plane-1][y][x]*erg[g]/erg_w[g])

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
        print "axial X/Y:", x, y

        axial = self.files[file_id].get_data(set_name)[:, y, x]
        fname = self.files[file_id].name

        # Mesh. At some point, derrive this from the actual data
        mesh = numpy.linspace(0.0, 1.0, len(axial))

        if self.axial_w is None:
            self.axial_w = Toplevel()
            self.axial_pa = PlotArea(self.axial_w)
            self.axial_pa.pack(fill=BOTH, expand=1)
            # Bind the window destruction protocol to the clear function
            self.axial_w.protocol("WM_DELETE_WINDOW", self.kill_axial)
        self.axial_pa.plot_line(mesh, axial, xlabel="Normalized Axial Height", label=fname+set_name)

    def kill_spect(self):
        self.spect_w.destroy()
        self.spect_w = None

    def kill_axial(self):
        self.axial_w.destroy()
        self.axial_w = None

    def change_scale_mode(self):
        self.controls.update_scales()
        self.plot()

    def select_file(self, file_id=-1):
        file_id = self.file_list.curselection()[0]
        self.file_id = file_id
        datasets = self.files[file_id].set_names

        self.data_list.delete(0, END)
        for i, dset in enumerate(datasets):
            self.data_list.insert(END, dset)

    def update_plot(self, plane):
        if self.current_plane != self.controls.plane():
            self.current_plane = self.controls.plane()
            self.plot()

    def plot(self, dummy=-1):
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]

        info = self.files[file_id].get_data_info(set_path)

        # Plot a space field of data (flux, correction factors, etc.)
        if info.datatype == "field":
            if info.ndim == 0:
                # Display scalar data
                data = self.files[file_id].get_data(set_path)
                self.scalarVar.set(set_path[1:] + ': ' + str(data))
            else:
                # Plot 2D data
                self.controls.update(info)

                data = self.files[file_id].get_data_2d(set_path, self.current_plane)
                self.nx = data.shape[0]
                self.ny = data.shape[1]

                min_ = None
                max_ = None

                # If we are doing global data scale, grab the scale bounds from the 3D
                # data before we flatten it. The other options will be taken care of
                # later.
                if self.controls.scale_mode.get() == 'global':
                    min_ = info.glb_min
                    max_ = info.glb_max
                elif self.controls.scale_mode.get() == 'manual':
                    min_ = float(self.controls.scale_min.get())
                    max_ = float(self.controls.scale_max.get())

                name = set_path.split('/')[-1]

                self.plot_area.plot(data, name, min_, max_)

        # Plot an angle
        if info.datatype == "angle":
            self.axial.update(1, info.n_planes)
            data = self.files[file_id].get_data(set_path)
            self.plot_area.plot_angle(data[self.current_plane-1, :])

        # Plot a line
        if info.datatype == "line":
            data = self.files[file_id].get_data(set_path)
            self.plot_area.plot_line(range(len(data)), data, logy=True)


    def update(self, files):
        self.files = files
        self.file_tree.update(self.files)
