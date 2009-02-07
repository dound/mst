import os, random

def quiet_remove(fn):
    try:
        os.remove(fn)
    except os.OSError:
        pass

def get_path_to_tools_root():
    """Gets the path to the root of the MST tools directory."""
    # strip off 'mstutil.py'
    if __file__[0:1] == '/':
        return __file__[:-10]
    else:
        return os.getcwd() + '/' + __file__[:-10]

def get_path_to_project_root():
    """Gets the path to the root of the MST project."""
    return get_path_to_tools_root()[:-6] # strip off 'tools/'

def get_path_to_mst_binary():
    """Gets the path to the mst solver binary."""
    return get_path_to_project_root() + 'src/mst'

def is_mst_binary_accessible():
    """Returns whether the mst solver binary can be accessed."""
    return os.access(get_path_to_mst_binary(), os.R_OK | os.X_OK)

def random_tmp_filename(sz):
    """Returns a random filename in the /tmp folder prefixed with 'dgu-'."""
    return "/tmp/dgu-" + random_filename(sz)

def random_filename(sz):
    """Returns a random string of the specified length composed of letters and/or numbers."""
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(sz)])

class FileFormatError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_tracked_revs():
    """Returns revisions we are tracking in an array of SHA1 revision IDs"""
    ret = []
    fh = open(get_path_to_tools_root() + 'conf/tracked_revs', "r")
    lines = fh.readlines()
    for line in lines:
        if line[0:1] != '#':
            s = line.split('\t', 4)
            if len(s) != 4:
                raise FileFormatError('line should have four columns (has %d): %s' % (len(s), line))
            ret.append(s[2])
    fh.close()
    return ret

if __name__ == "__main__":
    print get_path_to_project_root()
