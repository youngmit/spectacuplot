try:
    import pyvtk
    have_pyvtk = True
except:
    have_pyvtk = False
    StandardError("""The pyvtk package does not appear to be present. VTK
    visualization is disabled""")


class DataFile_VTK:
    thing=5