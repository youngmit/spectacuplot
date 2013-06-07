import h5py
import numpy
import os


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

        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)
            self.set_names = f.keys()
            self.ng = f['ng'].value[0]
        else:
            self.ng = self.f['ng'].value[0]
            self.set_names = self.f.keys()

    def get_name(self, data_id):
        return self.set_names[data_id]

    def get_erg(self):
        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)
            return f['eubounds'].value
        else:
            return self.f['eubounds'].value

    def get_data(self, data_id):
        if type(data_id) is int:
            data_name = self.set_names[data_id]
        else:
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
