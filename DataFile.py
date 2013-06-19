import h5py
import numpy
import os


class DataTreeNode:
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
    name = ""
    path = ""
    set_names = []
    composite = False
    ng = 0

    def __init__(self, name):
        self.composite = False
        self.path = name
        path = os.path.split(self.path)
        self.name = path[len(path)-1]
        self.f = h5py.File(self.path)

        self.set_names = self.f.keys()

        for n in self.set_names:
            if n == 'proc_map':
                self.proc_map = self.f['proc_map'].value
                self.n_proc = self.f['n_proc'].value[0]
                self.composite = True

        # Define f, the file object from which to find available datasets
        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)

        else:
            f = self.f

        self.set_names = f.keys()
        self.ng = f['ng'].value[0]

        self.data = DataTreeNode(f, '/')

        # print self.data

    def get_erg(self):
        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)
            return f['eubounds'].value
        else:
            return self.f['eubounds'].value

    def get_data(self, data_id):
        data_name = data_id

        if self.composite:
            # Blob all of the data together
            sub_data = []
            for f in xrange(self.n_proc):
                fname = self.path[:len(self.path)-3]
                fname = fname + '_n' + str(f) + '.h5'
                f = DataFile(fname)
                sub_data.append(f.get_data(data_name))

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
            return self.f[data_name].value

    def get_data_info(self, data_id):
        data = self.get_data(data_id)

        # Number of planes
        if numpy.ndim(data) == 3:
            shape = numpy.shape(data)
            planes = shape[0]
        else:
            planes = 1

        # Global min/max
        min_ = numpy.min(data)
        max_ = numpy.max(data)

        return DataInfo(n_planes=planes, max_=max_, min_=min_)

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


class DataInfo:
    def __init__(self, n_planes=None, max_=None, min_=None):
        self.n_planes = n_planes
        self.glb_max = max_
        self.glb_min = min_
