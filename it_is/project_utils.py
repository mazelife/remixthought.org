from os import path

def get_folder_path(dirname):
    """ Return the full path to the ``dirname`` in this directory."""
    here = path.dirname(__file__)
    return path.normpath(path.join(here, dirname))