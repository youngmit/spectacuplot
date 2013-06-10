from Tkinter import *

from PlotUtils import *

import numpy
import math

class OpDiffPlot(Frame):
    '''Plot tool for plotting the relative difference between two datasets.

    This too extends the Tk Frame class to insert a control panel for plotting
    the relative difference between two datasets. Two tree views of the opened
    files are provided, and the value that is plotted at each region is the
    local value of (left-right)/left. If the two datasets are different sizes,
    and the larger set can be fit cleanly into the smaller dataset, the larger
    dataset will be homogenized to conform to the coarser data.
    '''

    def __init__(self, master, files, plot_area, side=TOP):
        '''Constructor.

        Arguments:
        master -- the parent widget in which to embed the plot control.
        files -- a list of DataFile objects.
        plot_area -- a PlotArea widget to plot results to.

        Keyword arguments:
        side -- the side keyword to be supplied to Tk when the Frame is packed.
        '''
        Frame.__init__(self, master)

        self.plot_area = plot_area

        bottom_frame = Frame(self)
        bottom_frame.pack(side=BOTTOM, expand=1, fill=BOTH)

        left_frame = Frame(self)
        left_frame.pack(side=LEFT, expand=1, fill=BOTH)

        right_frame = Frame(self)
        right_frame.pack(side=LEFT, expand=1, fill=BOTH)

        self.left_tree = DataTree(left_frame)
        self.left_tree.tree.pack(expand=1, fill=BOTH)
        self.right_tree = DataTree(right_frame)
        self.right_tree.tree.pack(expand=1, fill=BOTH)

        self.plot_button = Button(bottom_frame, text="Plot Diff",
                                  command=self.plot)
        self.plot_button.pack()

        self.labelVar = StringVar()
        self.labelVar.set('RMS Error: ')
        label = Label(bottom_frame, textvariable=self.labelVar)
        label.pack()

    def update(self, files):
        self.left_tree.update(files)
        self.right_tree.update(files)

        self.files = files

    def plot(self):
        item = self.left_tree.tree.selection()[0]
        info = self.left_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]
        data1 = self.files[file_id].get_data(set_path)

        item = self.right_tree.tree.selection()[0]
        info = self.right_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]
        data2 = self.files[file_id].get_data(set_path)

        # Cast data to 2D
        if data1.ndim == 3:
            data1 = data1[:, :, 0]
        if data2.ndim == 3:
            data2 = data2[:, :, 0]

        # check dataset sizes
        data1_shape = numpy.shape(data1)
        data2_shape = numpy.shape(data2)

        if data1_shape[0] > data2_shape[0]:
            data1 = collapse_data(data1, data2)
        if data2_shape[0] > data1_shape[0]:
            data2 = collapse_data(data2, data1)

        data = (data1-data2) / data1

        rms = math.sqrt(sum(sum((data1-data2)**2))/numpy.size(data1))
        self.labelVar.set('RMS Error: ' + str(rms))

        self.plot_area.plot(data)


def collapse_data(large, small):
    shape_s = numpy.shape(small)
    shape_l = numpy.shape(large)
    width_s = shape_s[0]
    width_l = shape_l[0]

    if width_l % width_s != 0:
        raise Error

    ratio = width_l/width_s

    data = numpy.zeros(shape_s)
    for i in xrange(shape_l[0]):
        for j in xrange(shape_l[1]):
            row_s = i/ratio
            col_s = j/ratio
            data[row_s, col_s] = data[row_s, col_s]+large[i, j]
    data = data / ratio**2
    return data
