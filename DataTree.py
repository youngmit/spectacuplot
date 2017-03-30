from tkinter import *
from tkinter.ttk import Treeview

from DataFile import *


class DataTree(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg="black")
        scroll = Scrollbar(self)

        self.tree = Treeview(self, yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)

        self.items = []

        self.tree.pack(side=LEFT, fill=BOTH, expand=1)
        scroll.pack(side=LEFT, fill=Y)

    def update(self, files):
        self.files = files

        # reversing, since removing a node with children removes the children as
        # well. there might be a cleaner way to do this by clearing each of the
        # file nodes, but that might add more burden to the garbage collector
        # down the line.
        for item in reversed(self.items):
            self.tree.delete(item)

        self.items = []

        for (i, datafile) in enumerate(self.files):
            self.add_file(datafile, i)

    def add_file(self, f, f_id):
        file_id = self.tree.insert("", "end", text=f.name)
        self.items.append(file_id)

        self.add_node(file_id, f.data, f_id)

    def add_node(self, p, node, f_id):
        if node.name != '':
            node_id = self.tree.insert(p, "end", text=node.name,
                                       values=(f_id, node.path))
            self.items.append(node_id)
        else:
            node_id = p

        if node.is_grp:
            for child in node.children:
                self.add_node(node_id, child, f_id)


