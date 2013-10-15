import numpy
import h5py
import os

class DataTreeNode:
    '''Defines a single node in a data file tree.'''

    def __init__(self, f, name):
        self.path = name
        self.name = name.split('/')[-1]
        self.children = []

        # am I a group?
        cls = f.get(self.path, getclass=True)

        self.is_grp = (cls == h5py.Group)

        if self.is_grp:
            for child in f[self.path].keys():
                if self.path == '/':
                    new_name = self.path + child
                else:
                    new_name = self.path + '/' + child
                # print "adding node for ", new_name
                self.children.append(DataTreeNode(f, new_name))

    def print_children(self, outp, ind):
        if self.is_grp:
            outp = outp + ind*' ' + self.name + '\n'
            for child in self.children:
                outp = child.print_children(outp, ind+2)
        else:
            outp = outp + ind*' ' + self.name + '\n'

        return outp

    def __str__(self):
        ind = 0

        outp = self.name + 'Tree Root:'
        if self.is_grp:
            ind = ind + 2
            outp = self.print_children(outp, ind)

        return outp


class DataFile(object):
    '''base class for all filetypes. Mostly just exists to throw errors if a
       method is called that is not implemented by the derived class.
       '''

    name = ''

    def __init__(self, name):
        self.name = name
        self.has_mesh = False
        self.flip_y = False

    def get_erg(self):
        raise NotImplementedError('get_erg() is not implemented by this data file type!')

    def get_data(self, data_id):
        raise NotImplementedError('get_data() is not implemented by this data file type!')

    def get_data_2d(self, data_id, plane=None):
        raise NotImplementedError('get_data_2d() is not implemented by this data file type!')

    def get_data_info(self, data_id):
        raise NotImplementedError('get_data_info() is not implemented by this data file type!')


class DataInfo:
    '''Simple container class to store information about a dataset. Essentialy a
    struct.
    '''
    def __init__(self, data, planes=None):
        if numpy.ndim(data) == 1 and numpy.size(data) == 1:
            self.ndim = 0
        else:
            self.ndim = numpy.ndim(data)
        self.shape = numpy.shape(data)

        # Number of planes. If this is passed in, use that value, else use
        # leading order dimension
        if planes is None:
            if self.ndim >= 3:
                planes = self.shape[0]
            elif self.ndim == 2:
                planes = 1
            else:
                planes = 0

        # Global min/max
        self.n_planes = planes
        self.glb_max = numpy.max(data)
        self.glb_min = numpy.min(data)
