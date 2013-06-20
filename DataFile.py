import h5py
import numpy
import os


def OpenDataFile(name):
    '''Module-global routine to handle interrogation of a file for its format
    and to instantiate a data file object of the right type.
    '''

    # Figure out what type of file we are working with
    if(name.split('.')[-1]) == 'h5':
        h5f = h5py.File(name)
        f = None
        for s in h5f.keys():
            if s == 'core_map':
                print "MPACT Pin Power File"
                f = DataFilePinPower(name)
                break

        if f is None:
            # For now we are treating the MPACT Sn Vis file as the fallback.
            # Should use a more robust way of determining that it is valid.
            print "MPACT Sn Vis file"
            f = DataFileSnVis(name)
    return f


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


class DataFile:
    '''base class for all filetypes. Mostly just exists to throw errors if a
       method is called that is not implemented by the derived class.'''

    name = ''

    def __init__(self, name):
        self.name = name

    def get_erg(self):
        raise NotImplementedError('get_erg() is not implemented by this data file type!')

    def get_data(self, data_id):
        raise NotImplementedError('get_data() is not implemented by this data file type!')

    def get_data_2d(self, data_id, plane=None):
        raise NotImplementedError('get_data_2d() is not implemented by this data file type!')

    def get_data_info(self, data_id):
        raise NotImplementedError('get_data_info() is not implemented by this data file type!')


class DataFileH5(DataFile):
    path = ""
    set_names = []
    composite = False
    ng = 0

    def __init__(self, name):
        DataFile.__init__(self, name)

        self.path = name
        path = os.path.split(self.path)
        self.name = path[len(path)-1]
        self.f = h5py.File(self.path)

        self.set_names = self.f.keys()


class DataFilePinPower(DataFileH5):
    def __init__(self, name):
        DataFileH5.__init__(self, name)
        # Get the core map
        self.core_map = self.f['core_map'].value

        # Build the node tree
        self.data = DataTreeNode(self.f, '/')

    def get_data_2d(self, data_id, plane=None):
        if not plane is None:
            return self.get_data(data_id, plane)
        else:
            return self.get_data(data_id)

    def get_data(self, data_id, plane=1):
        raw_data = self.f[data_id].value
        raw_shape = numpy.shape(raw_data)

        core_shape = numpy.shape(self.core_map)

        blank = numpy.zeros([raw_shape[2], raw_shape[3]])

        # Construct the global array of data using the core map. Each row is
        # constructed as an hstack, then the core is built using a vstack of all
        # rows.
        rows = []
        for row in xrange(core_shape[1]):
            row_data = []
            for assem in self.core_map[row]:
                if assem > 0:
                    row_data.append(raw_data[assem-1, plane-1, :, :])
                else:
                    row_data.append(blank)
            rows.append(numpy.hstack(row_data))
        data = numpy.vstack((rows))
        # Reverse the rows, since the core is described upside down in natural
        # ordering
        # data_row = data

        return data

    def get_data_info(self, data_id):
        data = self.f[data_id].value

        shape = numpy.shape(data)
        planes = shape[1]

        # Global min/max
        min_ = numpy.min(data)
        max_ = numpy.max(data)

        return DataInfo(n_planes=planes, max_=max_, min_=min_)


class DataFileSnVis(DataFileH5):
    def __init__(self, name):
        DataFileH5.__init__(self, name)

        self.composite = False

        for n in self.set_names:
            if n == 'proc_map':
                self.proc_map = self.f['proc_map'].value
                self.n_proc = self.f['n_proc'].value[0]
                self.composite = True
                break

        # If we are using a composite file, override the set names with the
        # zero-th node set names.
        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)

        else:
            f = self.f

        self.data = DataTreeNode(f, '/')

        self.ng = f['ng'].value[0]

    def get_data(self, data_id):
        if self.composite:
            # Blob all of the data together
            sub_data = []
            for f in xrange(self.n_proc):
                fname = self.path[:len(self.path)-3]
                fname = fname + '_n' + str(f) + '.h5'
                f = DataFileSnVis(fname)
                sub_data.append(f.get_data(data_id))

            # for now, flatten the proc_map to a 2d thing
            proc_map = self.proc_map[0]
            # print proc_map
            rows = []
            for row in xrange(proc_map.shape[1]):
                row_data = []
                for node in proc_map[row]:
                    row_data.append(sub_data[node])
                rows.append(numpy.hstack(row_data))
            data = numpy.vstack(rows)

            return data

        else:
            return self.f[data_id].value

    def get_data_2d(self, data_id, plane=None):
        data = self.get_data(data_id)
        if numpy.ndim(data) == 3:
            shape = numpy.shape(data)
            if shape[2] > 1:
                if not plane is None:
                    data = data[plane-1, :, :]
                else:
                    data = data[0, :, :]
            else:
                data = data[:, :, 0]

        return data

    def get_data_info(self, data_id):
        data = self.get_data(data_id)

        # Number of planes
        if numpy.ndim(data) == 3:
            shape = numpy.shape(data)
            if shape[2] > 1:
                planes = shape[0]
            else:
                planes = 1
        else:
            planes = 1

        # Global min/max
        min_ = numpy.min(data)
        max_ = numpy.max(data)

        return DataInfo(n_planes=planes, max_=max_, min_=min_)

    def get_erg(self):
        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)
            return f['eubounds'].value
        else:
            return self.f['eubounds'].value


class DataInfo:
    '''Simple container class to store information about a dataset. Essentialy a
    struct.'''
    def __init__(self, n_planes=None, max_=None, min_=None):
        self.n_planes = n_planes
        self.glb_max = max_
        self.glb_min = min_
