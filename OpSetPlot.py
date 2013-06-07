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

        top_frame = Frame(self)
        top_frame.pack()

        bottom_frame = Frame(self)
        bottom_frame.pack()

        # File list
        file_frame = Frame(top_frame)
        file_frame.pack(side=LEFT, fill=Y, expand=1)
        Label(file_frame, text="Opened Files:").pack(side=TOP)
        self.file_list = Listbox(file_frame, selectmode=SINGLE)
        self.file_list.bind("<Double-Button-1>", self.select_file)
        self.file_list.pack(side=TOP)

        # Data selector
        data_frame = Frame(top_frame)
        data_frame.pack(side=LEFT, fill=Y, expand=1)
        Label(data_frame, text="Datasets:").pack(side=TOP)
        self.data_list = Listbox(data_frame)
        self.data_list.bind("<Double-Button-1>", self.plot)
        self.data_list.pack(side=TOP)

        self.plot_set = Button(bottom_frame, text="Plot Dataset",
                               command=self.plot)
        self.plot_set.pack(side=LEFT)

        # Spectrum plotting stuff
        print self.spectra.get()
        self.spect_toggle = Checkbutton(bottom_frame, text="Plot Spectra",
                                        command=self.toggle_spectra,
                                        variable=self.spectra, onvalue=True,
                                        offvalue=False)
        self.spect_toggle.pack(side=LEFT)
        print self.spectra.get()

    def toggle_spectra(self):
        if self.spectra.get():
            # Turn off spectra
            print "spectra on"
            self.cid = self.plot_area.canvas.mpl_connect('button_press_event',
                                                         self)
        else:
            # Turn on spectra
            print "spectra off"
            self.plot_area.canvas.mpl_disconnect(self.cid)

    # This is the spectrum plot function, which gets bound to click events on
    # the plot area.
    def __call__(self, event):
        print "click event", event
        if self.w is None:
            self.w = Toplevel()
            self.pa = PlotArea(self.w)
            self.pa.pack(fill=BOTH, expand=1)
            # Bind the window destruction protocol to the clear function
            self.w.protocol("WM_DELETE_WINDOW", self.kill_spect)

        # Get energy values
        erg = self.files[self.file_id].get_erg()
        erg_w = []
        prev_e = 0.0
        for e in reversed(erg):
            erg_w.append(e-prev_e)
            prev_e = e
        print "erg", erg
        erg_w.reverse()
        print erg_w
        print sum(erg_w)

        # Build array
        set_name = self.plot_area.label.get()
        set_pfx = set_name.split('_')[0]

        # get the index of the region that was clicked
        x = int(event.xdata)
        y = int(event.ydata)

        spect = []
        for g in xrange(self.files[self.file_id].ng):
            g_name = set_pfx + "_" + str(g+1).zfill(3)
            data = self.files[self.file_id].get_data(g_name)
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

    def plot(self, dummy=-1):
        data_id = self.data_list.curselection()[0]

        data = self.files[self.file_id].get_data(data_id)
        name = self.files[self.file_id].get_name(data_id)

        self.plot_area.plot(data, name)
