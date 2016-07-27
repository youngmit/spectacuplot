from Tkinter import *

from PlotArea import *

from PlotControls_3D import *
from PlotControls_1D import *

import numpy

class OpSetPlot(Frame):
    popout_w = None

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

        # Controls pane lives between the top and bottom pane. it needs a 
        # middle_frame container so that it doesnt move if the controls change
        self.middle_frame = Frame(self, relief=GROOVE, borderwidth=3, padx=5,
            pady=5)
        self.controls_frame = Frame(self.middle_frame, relief=SOLID)
        self.controls = PlotControls_3D(self.controls_frame, self)
        self.controls.pack(fill=BOTH)
        self.controls_frame.pack(fill=BOTH)
        self.middle_frame.pack(fill=BOTH)

        # Bottom pane just stores the scalar value viewer
        bottom_frame = Frame(self)
        bottom_frame.pack(fill=BOTH)

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
        pick_x = int(round(event.xdata))
        pick_y = int(round(event.ydata))

        if self.controls.pick_mode.get() == 'spectra':
            self.add_spectrum(event)
        elif self.controls.pick_mode.get() == 'value':
            item = self.file_tree.tree.selection()[0]
            info = self.file_tree.tree.item(item)
            file_id = info['values'][0]
            set_path = info['values'][1]

            data = self.files[file_id].get_data_2d(set_path, self.current_plane)
            index = self.nx*self.ny*(self.current_plane-1) + self.nx*pick_y + pick_x+1
            print pick_x, pick_y, self.current_plane, index, data[pick_y, pick_x]
        elif self.controls.pick_mode.get() == 'axial':
            self.add_axial(event)
        elif self.controls.pick_mode.get() == 'azimuthal':
            self.add_azimuthal(event)

    def add_azimuthal(self, event):
        pick_x = int(round(event.xdata))
        pick_y = int(round(event.ydata))
        
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]

        # Shave off the last section of the path, since we will be iterating
        # over it anyways
        path_decomp = set_path.split('/')[:-1]
        base_path = ""
        for s in path_decomp:
            base_path += s + "/"
        print base_path
        
        # get angles
        (azimuthal, polar) = self.files[file_id].get_angles()
        # crop to the pozitive half-space
        n_polar = len(polar)
        n_azi = len(azimuthal)

        # For now, only look at the first polar angle
        values = numpy.zeros(n_azi)

        file = self.files[file_id]

        for (i, idata) in enumerate(xrange(0, n_polar*n_azi, n_polar)):
            path = base_path + str(idata).zfill(3)
            values[i] = file.get_data_2d(path, self.current_plane)[pick_y, pick_x]
        
        # sort for increasing azimuthal
        azimuthal, values = (list(x) for x in zip(*sorted(zip(azimuthal,values))))
        azimuthal.append(azimuthal[0])
        values.append(values[0])
        
        self.spawn_popout(axes="polar")

        self.popout_pa.plot_line(azimuthal, values)
        
        
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
        x = int(round(event.xdata))
        y = int(round(event.ydata))

        spect = []
        for g in xrange(self.files[file_id].ng):
            g_name = set_pfx + "/" + str(g+1).zfill(3)
            data = self.files[file_id].get_data(g_name)
            spect.append(data[self.current_plane-1][y][x]*erg[g]/erg_w[g])

        self.spawn_popout(axes="polar")

        self.popout_pa.plot_line(erg, spect, logx=True)

    def add_axial(self, event):
        # Get energy values
        item = self.file_tree.tree.selection()[0]
        info = self.file_tree.tree.item(item)
        file_id = info['values'][0]

        # Build array
        set_name = info['values'][1]

        # get the index of the region that was clicked
        x = int(round(event.xdata))
        y = int(round(event.ydata))
        print "axial X/Y:", x, y

        axial = self.files[file_id].get_data(set_name)[:, y, x]
        fname = self.files[file_id].name

        # Mesh. At some point, derrive this from the actual data
        mesh = numpy.linspace(0.0, 1.0, len(axial))

        self.spawn_popout()

        print axial
        self.popout_pa.plot_line(mesh, axial, xlabel="Normalized Axial Height",
                                ylabel=set_name,
                                label=fname+set_name)

    def spawn_popout(self, axes="lin"):
        print "Making a new popout window"
        if self.popout_w is None:
            self.popout_w = Toplevel()
            self.popout_pa = PlotArea(self.popout_w, axes)
            self.popout_pa.pack(fill=BOTH, expand=1)
            # Bind the window destruction protocol to the clear function
            self.popout_w.protocol("WM_DELETE_WINDOW", self.kill_popout)

    def kill_popout(self):
        self.popout_w.destroy()
        self.popout_w = None

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

    def change_1d(self):
        logx = (self.controls.x_type.get() == 'log')
        logy = (self.controls.y_type.get() == 'log')
        self.plot_area.set_log(logx, logy)

    def reset_1d(self):
        self.plot_area.reset()


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
                # Switch to the 2D/3D controls if necessary
                if not isinstance(self.controls, PlotControls_3D):
                    self.controls_frame.destroy()
                    self.controls_frame = Frame(self.middle_frame, relief=SUNKEN)
                    self.controls = PlotControls_3D(self.controls_frame, self)
                    self.controls.pack(fill=BOTH)
                    self.controls_frame.pack(fill=BOTH)
                    self.plot_area.reset()
                    # Register plot with callback
                    self.cid = self.plot_area.canvas.mpl_connect('button_press_event',
                                                     self.pick)
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
            # Switch to the line plot controls if necessary
            if not isinstance(self.controls, PlotControls_1D):
                self.controls_frame.destroy()
                self.controls_frame = Frame(self.middle_frame, relief=SUNKEN)
                self.controls = PlotControls_1D(self.controls_frame, self)
                self.controls.pack(fill=BOTH)
                self.controls_frame.pack(fill=BOTH)
                self.plot_area.reset()

            data = self.files[file_id].get_data(set_path)
            # Look for abscissae
            x_label = "X"
            if self.controls.custom_abscissa():
                abscissa_path = '/'.join(set_path.split('/')[:-1]+["abscissae"])
                try:
                    abscissae = self.files[file_id].get_data(abscissa_path)
                    x_label = "Time (s)"
                except:
                    abscissae = range(len(data))
            else:
                abscissae = range(len(data))
            label = self.files[file_id].name + ": " + (set_path.split("/")[-1])
            y_label = set_path.split("/")[-1]
            self.plot_area.plot_line(abscissae, data, label=label, xlabel=x_label, ylabel=y_label)


    def update(self, files):
        self.files = files
        self.file_tree.update(self.files)
