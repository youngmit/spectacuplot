from Tkinter import *

class PlotControls_1D(Frame):
    def __init__(self, master, consumer):
        Frame.__init__(self, master)

        axis_frame = Frame(self)
        
        self.x_type = StringVar()
        self.x_type.set('linear')

        axis_frame_x = Frame(axis_frame)
        Label(axis_frame_x, text="X Axis:").pack(anchor=W)
        Radiobutton(axis_frame_x, text="Linear", variable=self.x_type,
                    value='linear', command=consumer.change_1d).pack(side=TOP, anchor=W)
        Radiobutton(axis_frame_x, text="Log", variable=self.x_type,
                    value='log', command=consumer.change_1d).pack(side=TOP, anchor=W)
        axis_frame_x.pack(side=LEFT)

        self.y_type = StringVar()
        self.y_type.set('linear')

        axis_frame_y = Frame(axis_frame)
        Label(axis_frame_y, text="Y Axis:").pack(anchor=W)
        Radiobutton(axis_frame_y, text="Linear", variable=self.y_type,
                    value='linear', command=consumer.change_1d).pack(side=TOP, anchor=W)
        Radiobutton(axis_frame_y, text="Log", variable=self.y_type,
                    value='log', command=consumer.change_1d).pack(side=TOP, anchor=W)
        axis_frame_y.pack()

        axis_frame.pack()

        Button(self, text="Reset", command=consumer.reset_1d).pack()
