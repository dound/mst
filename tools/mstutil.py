import os, random, sys

def compare_float(f1, f2):
    if f1 < f2:
        return -1
    elif f1 > f2:
        return 1
    else:
        return 0

def die(errmsg):
    """Prints the message to stderr and then exits with error code -1."""
    print >> sys.stderr, errmsg
    sys.exit(-1)

def quiet_remove(fn):
    try:
        os.remove(fn)
    except OSError:
        pass

def get_path_to_tools_root():
    """Gets the path to the root of the MST tools directory."""
    # strip off 'mstutil.py'
    d = os.path.dirname(__file__) + '/'
    if __file__[0:1] == '/':
        return d
    else:
        return os.getcwd() + '/' + d

def get_path_to_project_root():
    """Gets the path to the root of the MST project."""
    return get_path_to_tools_root()[:-6] # strip off 'tools/'

def get_path_to_mst_binary():
    """Gets the path to the mst solver binary."""
    return get_path_to_project_root() + 'src/mst'

def get_path_to_checker_binary(make_sure_it_exists=False):
    """Gets the path to our correctness checker."""
    d = get_path_to_tools_root() + 'checker/'
    path = d + 'boost_compute_mst_weight'
    if make_sure_it_exists:
        os.system('make -C %s > /dev/null' % d)
    return path

def get_path_to_generated_inputs():
    """Gets the path to a symlink to the generated input graphs stored in /tmp/<user>-gen."""
    real_path = '/tmp/' + os.getlogin() + '-gen/'
    if not os.path.exists(real_path):
        os.mkdir(real_path)

    symlink = get_path_to_project_root() + 'input/gen'
    if not os.path.exists(symlink):
        os.symlink(real_path, symlink)

    return symlink + '/'

def is_mst_binary_accessible():
    """Returns whether the mst solver binary can be accessed."""
    return os.access(get_path_to_mst_binary(), os.R_OK | os.X_OK)

def random_tmp_filename(sz):
    """Returns a random filename in the /tmp folder prefixed with 'dgu-'."""
    return "/tmp/dgu-" + random_filename(sz)

def random_filename(sz):
    """Returns a random string of the specified length composed of letters and/or numbers."""
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(sz)])

if __name__ == "__main__":
    print get_path_to_project_root()
