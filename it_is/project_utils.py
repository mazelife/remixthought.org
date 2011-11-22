from os import path

def get_folder_path(dirname):
    """ Return the full path to the ``dirname`` in this directory."""
    here = path.dirname(__file__)
    return path.normpath(path.join(here, dirname))


def get_env_setting(env, setting_name, default=None):
    return env.get(setting_name, default)
