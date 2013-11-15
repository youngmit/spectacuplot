from DataFile_Base import *
import h5py


class DataFileH5(DataFile):
    '''Semi-virtual class for defining basic HDF5 functionality. It provides a
    basic get_data implementation, which returns a dataset as-is from the HDF5
    file. This routine may be overridden by inheriting classes, of course.
    '''

    path = ""
    set_names = []
    composite = False
    ng = 0
    # This will be the HDF5 File object
    f = None

    def __init__(self, name):
        DataFile.__init__(self, name)

        self.path = name
        path = os.path.split(self.path)
        self.name = path[len(path)-1]
        self.f = h5py.File(self.path)

        self.set_names = self.f.keys()

    def get_data(self, data_id):
        '''Return a raw set of data from the HDF5 file. If it is really
        multidimensional, it will return the data as-is. If it appears to be a
        scalar, it will be returned as such.'''

        data = self.f[data_id].value
        if numpy.ndim(data) == 1 and numpy.size(data) == 1:
            return data[0]
        else:
            return data


class DataFilePinPower(DataFileH5):
    '''Fully implemented data file class for interacting with pin power files.
    It uses the base H5 class to retrieve data from the file, and get_data_2d
    assembles core-global data using the core_map dataset.'''

    def __init__(self, name):
        DataFileH5.__init__(self, name)
        # Get the core map
        self.core_map = self.f['core_map'].value.T

        self.sym=self.f['core_sym'].value[0]

        if(self.f['core_sym'].value[0] == '4'):
            nxcore=numpy.shape(self.core_map)[0]
            nycore=numpy.shape(self.core_map)[1]
            if(nxcore != nycore):
                raise StandardError("Only square core supported at present")

        # Build the node tree
        self.data = DataTreeNode(self.f, '/')

    def get_data_2d(self, data_id, plane=None):
        raw_data = self.get_data(data_id)
        if plane is None:
            plane = 1

        raw_shape = numpy.shape(raw_data)

        core_shape = numpy.shape(self.core_map)

        blank = numpy.zeros([raw_shape[0], raw_shape[1]])

        # Construct the global array of data using the core map. Each row is
        # constructed as an hstack, then the core is built using a vstack of all
        # rows.
        rows = []
        if(self.sym == 4):
            for row in xrange(core_shape[0]):
                l_flip_y = False
                if row < core_shape[0]/2:
                    l_flip_y = True
                row_data = []
                for (col, assem) in enumerate(self.core_map[row]):
                    l_flip_x = False
                    if col < core_shape[1]/2:
                        l_flip_x = True
                    if assem > 0:
                        assem_data = raw_data[:, :, plane-1, assem-1]
                        if l_flip_x:
                            assem_data = assem_data[::-1, :]
                        if l_flip_y:
                            assem_data = assem_data[:, ::-1]
                        row_data.append(assem_data)
                    else:
                        row_data.append(blank)
                rows.append(numpy.vstack(row_data))
            data = numpy.hstack((rows))

        else:
            for row in xrange(core_shape[0]):
                row_data = []
                for assem in self.core_map[row]:
                    if assem > 0:
                        row_data.append(raw_data[:, :, plane-1, assem-1])
                    else:
                        row_data.append(blank)
                rows.append(numpy.vstack(row_data))
            data = numpy.hstack((rows))
        return data

    def get_data_info(self, data_id):
        '''This data file format stores data by plane in dimension 1 (dimension
        2 if you use one-based indexing). Use that value from the shape.'''

        data = self.f[data_id].value
        planes = None
        shape = numpy.shape(data)

        if len(shape) == 4:
            planes = shape[2]
        return DataInfo(data, planes)


class DataFileSnVis(DataFileH5):
    '''Fully implemented class for interacting with HDF5 datafiles from my Sn
    sweeper. The files can be either atomic (written by a single MPI node), or
    composite (multiple files written by several MPI nodes). To get around the
    drastically different needs for reading these collections of files, the
    get_data routine from the HDF5 data file class is overridden to properly
    assemble raw datasets from the component HDF5 files.'''

    def __init__(self, name):
        DataFileH5.__init__(self, name)

        self.composite = False
        self.flip_y = True

        if self.f.attrs.get('noflip') == 1:
            self.flip_y = False

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

        try:
            self.ng = f['ng'].value[0]
        except:
            self.ng = 0

    def get_data(self, data_id):
        '''Overrides the get_data function on the HDF5 file class. This is to
        allow for it to handle composite datasets, which are generated by
        multiple MPI processes. It will return the entire dataset, properly
        assembled as if it were written by a single process.
        '''
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
            # Defer to the superclass get_data routine
            data = super(DataFileSnVis, self).get_data(data_id)
            # flip the data along the y axis, because nuclear engineers make no
            # sense.
            sh = numpy.shape(data)
            if len(sh) == 3:
                if self.flip_y:
                    return data[:, ::-1, :]
                else:
                    return data
            elif len(sh) == 2:
                if self.flip_y:
                    return data[::-1, :]
                else:
                    return data

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
                data = data[0, :, :]
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

        return DataInfo(data, planes=planes)

    def get_erg(self):
        '''Returns the upper bounds of the energy groups in the data file. It is
        assumed that these bounds are stored in a dataset named eubounds. If
        such a dataset does not exist, an exception is raised.'''
        if self.composite:
            fname = self.path[:len(self.path)-3]
            fname = fname + '_n0' + '.h5'
            f = h5py.File(fname)
            try:
                return f['eubounds'].value
            except:
                raise StandardError('There does not appear to be any energy ' +
                                    'structure information in this data file.')
        else:
            try:
                return self.f['eubounds'].value
            except:
                raise StandardError('There does not appear to be any energy ' +
                                    'structure information in this data file.')
