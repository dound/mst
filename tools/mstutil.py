import os, random

def quiet_remove(fn):
    try:
        os.remove(fn)
    except OSError:
        pass

def get_path_to_tools_root():
    """Gets the path to the root of the MST tools directory."""
    # strip off 'mstutil.py'
    dir = os.path.dirname(__file__) + '/'
    if __file__[0:1] == '/':
        return dir
    else:
        return os.getcwd() + '/' + dir

def get_path_to_project_root():
    """Gets the path to the root of the MST project."""
    return get_path_to_tools_root()[:-6] # strip off 'tools/'

def get_path_to_mst_binary():
    """Gets the path to the mst solver binary."""
    return get_path_to_project_root() + 'src/mst'

def get_path_to_inputs():
    """Gets the path to the input graphs."""
    return get_path_to_project_root() + 'input/'

def get_path_to_correctness_results(rev=''):
    """Gets the path to the correctness results."""
    return get_path_to_project_root() + 'result/corr/' + rev

def get_path_to_performance_results(rev=''):
    """Gets the path to the performance results."""
    return get_path_to_project_root() + 'result/perf/' + rev

def get_path_to_weight_results(wtype=''):
    """Gets the path to the weight results."""
    return get_path_to_project_root() + 'result/weight/' + wtype

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

def get_tracked_inputs():
    """Returns input graphs we are tracking as an array of filenames"""
    ret = []
    for root, _, files in os.walk(get_path_to_inputs()):
        for name in files:
            ret.append(os.path.join(root, name))
    return ret

def get_tracked_revs():
    """Returns revisions we are tracking as an array of SHA1 revision IDs"""
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

def __get_results(path, str_to_val, str_val_type):
    """Returns a dictionary which maps input names to arrays of results in rev"""
    results = {}
    fh = open(path, "r")
    lines = fh.readlines()
    for line in lines:
        if line[0:1] != '#':
            s = line.split()
            if len(s) != 2:
                raise FileFormatError('line should have two columns (has %d): %s' % (len(s), line))
            input_val = s[0]
            try:
                t = str_to_val(s[1])
            except ValueError:
                raise FileFormatError('line should have a %s value: %s' % (str_val_type, line))

            if results.has_key(input_val):
                results[input_val].append(t)
            else:
                results[input_val] = [t]
    fh.close()
    return results

def get_correctness_results(rev):
    """Returns a dictionary which maps input names to arrays of booleans in rev"""
    return __get_results(get_path_to_correctness_results(rev), bool, "boolean")

def get_performance_results(rev):
    """Returns a dictionary which maps input names to arrays of float runtimes in rev"""
    return __get_results(get_path_to_performance_results(rev), float, "floating-point")

def get_weight_results(wtype):
    """Returns a dictionary which maps input names to arrays of float weights in rev"""
    return __get_results(get_path_to_weight_results(wtype), float, "float")

if __name__ == "__main__":
    print get_path_to_project_root()
