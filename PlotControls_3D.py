from Tkinter import *

from AxialSlider import *
from LabeledEntry import *

class PlotControls_3D(Frame):
    def __init__(self, master, consumer):
        Frame.__init__(self, master)

        pick_mode_frame = Frame(self)
        pick_mode_frame.pack(side=TOP)

        slider_frame = Frame(self)
        slider_frame.pack(side=TOP, fill=BOTH)

        scale_frame = Frame(self)
        scale_frame.pack(side=LEFT, expand=1, fill=BOTH)

        # pick mode radio buttons
        self.pick_mode = StringVar()
        self.pick_mode.set('value')

        Radiobutton(pick_mode_frame, text="Value", variable=self.pick_mode,
                    value='value').pack(side=LEFT, anchor=W)
        Radiobutton(pick_mode_frame, text="Spectra", variable=self.pick_mode,
                    value='spectra').pack(side=LEFT, anchor=W)
        Radiobutton(pick_mode_frame, text="Axial", variable=self.pick_mode,
                    value='axial').pack(side=LEFT, anchor=W)

        # Axial Slider
        Label(slider_frame, text="Axial plane:").pack(anchor=W)
        self.axial = AxialSlider(slider_frame, command=consumer.update_plot)
        self.axial.pack(side=BOTTOM, expand=1, fill=BOTH)

        # Scale selector
        Label(scale_frame, text="Color Scale:").pack(anchor=W)
        self.scale_mode = StringVar()
        self.scale_mode.set('active')
        self.scale_plane = StringVar()
        Radiobutton(scale_frame, text="Active Plane", variable=self.scale_mode,
                    value='active', command=consumer.change_scale_mode).pack(side=LEFT, anchor=W)
        Radiobutton(scale_frame, text="Global", variable=self.scale_mode,
                    value='global', command=consumer.change_scale_mode).pack(side=LEFT, anchor=W)
        Radiobutton(scale_frame, text="Manual", variable=self.scale_mode,
                    value='manual', command=consumer.change_scale_mode).pack(side=LEFT, anchor=W)
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

    def plane(self):
        return self.axial.get()

    def set_nplanes(self, n_planes):
        self.axial.update(1, n_planes)

    def update(self, info):
        self.axial.update(1, info.n_planes)

    def update_scales(self):
        if self.scale_mode.get() == 'manual':
            self.scale_min_entry.enable()
            self.scale_max_entry.enable()
        else:
            self.scale_min_entry.disable()
            self.scale_max_entry.disable()

