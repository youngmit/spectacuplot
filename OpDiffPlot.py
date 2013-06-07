from Tkinter import *

from PlotUtils import *


class OpDiffPlot(Frame):
    def __init__(self, master, files, plot_area, side=TOP):
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

        data = (data1-data2)/data1
        self.plot_area.plot(data)
