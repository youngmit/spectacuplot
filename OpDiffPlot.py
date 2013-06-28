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
        self.left_tree.pack(expand=1, fill=BOTH)
        self.right_tree = DataTree(right_frame)
        self.right_tree.pack(expand=1, fill=BOTH)

        self.plot_button = Button(bottom_frame, text="Plot Diff",
                                  command=self.plot)
        self.plot_button.pack()

        self.rmsVar = StringVar()
        self.rmsVar.set('RMS Error: ')
        Label(bottom_frame, textvariable=self.rmsVar).pack(anchor=W)
        self.maxVar = StringVar()
        self.maxVar.set('Max: ')
        Label(bottom_frame, textvariable=self.maxVar).pack(anchor=W)

    def update(self, files):
        self.left_tree.update(files)
        self.right_tree.update(files)

        self.files = files

    def plot(self):
        item = self.left_tree.tree.selection()[0]
        info = self.left_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]
        data1 = self.files[file_id].get_data_2d(set_path)

        item = self.right_tree.tree.selection()[0]
        info = self.right_tree.tree.item(item)
        file_id = info['values'][0]
        set_path = info['values'][1]
        data2 = self.files[file_id].get_data_2d(set_path)

        # check dataset sizes
        data1_shape = numpy.shape(data1)
        data2_shape = numpy.shape(data2)

        if data1_shape[0] != data2_shape[0]:
            (data1, data2) = collapse_data(data1, data2)

        data = (data1-data2) / data1

        non_zeros = numpy.count_nonzero(data1-data2)
        rms = math.sqrt(sum(sum((data1-data2)**2))/non_zeros)
        self.rmsVar.set('RMS Error: ' + str(rms))
        self.maxVar.set('Max: ' + str(numpy.nanmax(abs(data))))

        self.plot_area.plot(data, label='Relative Difference')


def collapse_data(data1, data2):
    shape_1 = numpy.shape(data1)
    shape_2 = numpy.shape(data2)
    width_1 = shape_1[0]
    width_2 = shape_2[0]

    # Determine the greatest common factor to homogenize by
    g1 = gcf(shape_1[0], shape_2[0])
    g2 = gcf(shape_1[1], shape_2[1])
    if shape_1[0]/g1 != shape_1[1]/g2:
        raise StandardError('Could not determine a consistent GCF.')

    # homogenize data1
    ratio = width_1/g1
    data1h = numpy.zeros([g1, g2])
    for i in xrange(shape_1[0]):
        for j in xrange(shape_1[1]):
            row = i/ratio
            col = j/ratio
            data1h[row, col] = data1h[row, col] + data1[i, j]
    data1h = data1h/(ratio*ratio)
    # homogenize data2
    ratio = width_2/g1
    data2h = numpy.zeros([g1, g2])
    for i in xrange(shape_2[0]):
        for j in xrange(shape_2[1]):
            row = i/ratio
            col = j/ratio
            data2h[row, col] = data2h[row, col] + data2[i, j]
    data2h = data2h/(ratio*ratio)

    return (data1h, data2h)


def gcf(a, b):
    f = 1
    while f != 0:
        l = max(a, b)
        s = min(a, b)
        f = l % s
        a = s
        b = f
    return a
