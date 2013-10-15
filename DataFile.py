import h5py
from DataFile_H5 import DataFilePinPower,DataFileSnVis
from DataFile_VTK import DataFile_VTK


def OpenDataFile(name):
    '''Module-global routine to handle interrogation of a file for its format
    and to instantiate a data file object of the right type.
    '''

    # Figure out what type of file we are working with
    ext = name.split('.')[-1]
    if ext == 'h5':
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
    elif ext == "vtk":
        print "VTK files"

    return f