import os, random

def get_path_to_project_root():
    """Gets the path to the root of the MST project."""
    return os.getcwd() + '/../'

def get_path_to_mst_binary():
    """Gets the path to the mst solver binary."""
    return os.getcwd() + '/../src/mst'

def is_mst_binary_accessible():
    """Returns whether the mst solver binary can be accessed."""
    return os.access(get_path_to_mst_binary(), os.R_OK | os.X_OK)

def random_tmp_filename(len):
    """Returns a random filename in the /tmp folder prefixed with 'dgu-'."""
    return "/tmp/dgu-" + random_filename(len)

def random_filename(len):
    """Returns a random string of the specified length composed of letters and/or numbers."""
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(len)])
