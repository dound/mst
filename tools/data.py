from mstutil import compare_float, get_path_to_generated_inputs, get_path_to_project_root, get_path_to_tools_root
import os, re

# whether to return pretty-printed input paths quickly or with more helpful info
FAST_INPUT_PATH_PRETTY_PRINT = False

class DataError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class DataSet:
    """A collection of Data objects"""
    def __init__(self, dataset):
        self.dataset = dataset

    def add_data(self, data):
        """Inserts or updates the dataset and returns true if anything changed."""
        key = data.mykey()
        if self.dataset.has_key(key):
            old = self.dataset[key]
            if old == data:
                return False
        self.dataset[key] = data
        return True

    def save_to_file(self, logfn):
        """Saves the dataset to the specified log file in sorted order"""
        sorted_data = sorted(self.dataset.values())
        try:
            fh = open(logfn, "w")
            if len(sorted_data) > 0:
                fh.write(sorted_data[0].header_row() + '\n')
            for d in sorted_data:
                fh.write('%s\n' % str(d))
            fh.close()
        except IOError, e:
            raise DataError("I/O error while writing to %s: %s" % (logfn, e))

    @classmethod
    def read_from_file(cls, cls_data, logfn, mustExist=False):
        """Factory method which populates a DataSet composed of cls_data
        type objects with the contents of a file."""
        dataset = {}
        if not mustExist and not os.path.exists(logfn):
            return cls(dataset)
        try:
            fh = open(logfn, "r")
            lines = fh.readlines()
            for line in lines:
                if line[0:1] != '#':
                    s = line.split()
                    t = cls_data.from_list(s)
                    dataset[t.mykey()] = t
            fh.close()
        except IOError, e:
            raise DataError("I/O error while reading in %s: %s" % (logfn, e))
        except ValueError, e:
            fh.close()
            raise DataError("Improper value encountered while reading in %s: %s" % (logfn, e))
        return cls(dataset)

    @classmethod
    def add_data_to_log_file(cls, data, logfn=None):
        """Adds data to the appropriate log file."""
        if logfn is None:
            logfn = data.get_path()
        ds = cls.read_from_file(data.__class__, logfn)
        if ds.add_data(data):
            ds.save_to_file(logfn)

class Input:
    """Data based on some input"""
    def __init__(self, prec, dims, min_val, max_val, num_verts, num_edges, seed):
        self.prec      = int(prec)
        self.dims      = int(dims)
        self.min       = float(min_val)
        self.max       = float(max_val)
        self.num_verts = int(num_verts)
        self.num_edges = int(num_edges)
        self.seed      = int(seed)

    def get_wtype(self):
        if self.prec!=15 or self.min!=0 or self.max!=1:
            return None
        if self.dims > 0:
            return 'loc%u' % self.dims
        else:
            return 'edge'

    def make_args_for_generate_input(self):
        """Returns a string which can  be used to make generate_input.py generate this input."""
        argstr = '-p %u -n %u %u -r %s' % (self.prec, self.num_edges, self.num_verts, str(self.seed))
        if self.dims == 0 and (self.min!=0 or self.max!=100000):
            argstr += ' -e %.1f,%.1f' % (self.min, self.max)
        elif self.dims > 0:
            argstr += ' -v %u,%.1f,%.1f' % (self.dims, self.min, self.max)
        return argstr

    def __cmp__(self, other):
        """Provides some ordering on Input"""
        if self.prec != other.prec:
            return self.prec - other.prec
        if self.dims != other.dims:
            return self.dims - other.dims
        if self.min < other.min:
            return -1
        if self.min > other.min:
            return 1
        if self.max < other.max:
            return -1
        if self.max > other.max:
            return 1
        if self.num_verts != other.num_verts:
            return self.num_verts - other.num_verts
        if self.num_edges != other.num_edges:
            return self.num_edges - other.num_edges
        if self.seed < other.seed:
            return -1
        if self.seed > other.seed:
            return 1
        return 0

    def __hash__(self):
        """Simple hash on vertices, edges, and the seed"""
        ret = self.num_verts
        ret = ret * 31 + self.num_edges
        return ret * 31 + self.seed

    def __str__(self):
        return "%s %u %s %s %u %u %s" % (str(self.prec), self.dims, str(self.min), str(self.max),
                                         self.num_verts, self.num_edges, str(self.seed))

class AbstractData:
    def __init__(self, prec, dims, min_val, max_val, num_verts, num_edges, seed):
        self.__input = Input(prec, dims, min_val, max_val, num_verts, num_edges, seed)

    def input(self):
        return self.__input

    def mykey(self):
        return self.__input

    def __cmp__(self, other):
        return self.input().__cmp__(other.input())

    def __hash__(self):
        return self.input().__hash__()

    def __str__(self):
        return self.input().__str__()

class InputSolution(AbstractData):
    """Data about about how to generate an input and the MST weight of that input (if known)."""
    def __init__(self, prec, dims, min_val, max_val, num_verts, num_edges, seed, mst_weight='-1'):
        AbstractData.__init__(self, prec, dims, min_val, max_val, num_verts, num_edges, seed)
        self.mst_weight = float(mst_weight)

    def get_path(self):
        i = self.input()
        return InputSolution.get_path_to(i.prec, i.dims, i.min, i.max)

    def has_mst_weight(self):
        """Whether the MST weight is known for this input"""
        return self.mst_weight >= 0

    def update_mst_weight(self, w):
        """Updates the mst_weight field (returns True if any changes occur)"""
        if self.mst_weight != w:
            self.mst_weight = w
            return True
        else:
            return False

    def __cmp__(self, other):
        ret = AbstractData.__cmp__(self, other)
        if ret != 0:
            return ret
        else:
            return compare_float(self.mst_weight, other.mst_weight)

    def __str__(self):
        return AbstractData.__str__(self) + ' ' + str(self.mst_weight)

    @staticmethod
    def header_row():
        return "#Prec Dim Min Max |V| |E| Seed MSTWeight"

    @staticmethod
    def key(prec, dims, min_val, max_val, num_verts, num_edges, seed):
        return Input(prec, dims, min_val, max_val, num_verts, num_edges, seed)

    @staticmethod
    def from_list(lst):
        if(len(lst) != 8):
            raise DataError('InputSolution expected 8 args, got %u: %s' % (len(lst), str(lst)))
        return InputSolution(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], lst[6], lst[7])

    @staticmethod
    def get_path_to(prec, dims, min_val, max_val):
        may_be_part2_input = (prec==15 and min_val==0 and max_val==1)
        if dims == 0:
            if prec==1 and min_val==0 and max_val==100000:
                logbasename = 'perf.inputs'
            elif may_be_part2_input:
                logbasename = 'p2-redge.inputs'
            else:
                logbasename = 'other-redge.inputs'
        else:
            if may_be_part2_input and dims>=2 and dims<=4:
                logbasename = 'p2-rvert-%ud.inputs' % dims
            else:
                logbasename = 'other-rvert.inputs'
        return get_path_to_project_root() + 'input/' + logbasename

class AbstractResult(AbstractData):
    """Data about an input and a revision on which we ran a test on it."""
    def __init__(self, prec, dims, min_val, max_val, num_verts, num_edges, seed, rev, run_num):
        AbstractData.__init__(self, prec, dims, min_val, max_val, num_verts, num_edges, seed)
        self.rev = str(rev)
        self.run_num = run_num

    def get_path(self):
        return self.get_path_to(self.rev)

    def mykey(self):
        return (self.__input, self.run_num)

    def __cmp__(self, other):
        ret = AbstractData.__cmp__(self, other)
        if ret != 0:
            return ret
        elif self.rev < other.rev:
            return -1
        elif self.rev > other.rev:
            return 1
        else:
            return self.run_num - other.run_num

    @staticmethod
    def get_path_to(rev):
        raise DataError('get_path_to should be overriden in AbstractResult children')

CORRECT = int(True)
INCORRECT = int(False)
class CorrResult(AbstractResult):
    """Data about an input, a revision, and whether mst correctly found the MST."""
    def __init__(self, dims, min_val, max_val, num_verts, num_edges, seed, rev, run_num, corr):
        AbstractResult.__init__(self, 1, dims, min_val, max_val, num_verts, num_edges, seed, rev, run_num)
        corr = int(corr)
        if corr!=CORRECT and corr!=INCORRECT:
            raise ValueError('invalid corr value: ' + str(corr))
        self.corr = corr

    def is_correct(self):
        return self.corr == CORRECT

    def __cmp__(self, other):
        ret = AbstractResult.__cmp__(self, other)
        if ret != 0:
            return ret
        else:
            return (0 if self.corr==other.corr else (1 if self.corr else -1))

    def __str__(self):
        i = self.input()
        return "%s %u %s %s %u %u %s %u %u" % (str(i.prec), i.dims, str(i.min), str(i.max),
                                               i.num_verts, i.num_edges, str(i.seed), self.run_num, int(self.corr))

    @staticmethod
    def header_row():
        return "#Prec Dim Min Max |V| |E| Seed Run# Correct?"

    @staticmethod
    def key(dims, min_val, max_val, num_verts, num_edges, seed, run_num):
        return (Input(1, dims, min_val, max_val, num_verts, num_edges, seed), run_num)

    @staticmethod
    def from_list(lst):
        if(len(lst) != 9):
            raise DataError('CorrResult expected 9 args, got %u: %s' % (len(lst), str(lst)))
        return CorrResult(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], lst[6], lst[7], lst[8])

    @staticmethod
    def get_path_to(rev):
        return get_path_to_project_root() + 'result/corr/' + rev

class PerfResult(AbstractResult):
    """Data about an input, a revision, and how quickly it found the MST."""
    def __init__(self, num_verts, num_edges, seed, rev, run_num, time_sec):
        AbstractResult.__init__(self, 1, 0, 0, 100000, num_verts, num_edges, seed, rev, run_num)
        self.time_sec = float(time_sec)

    def __cmp__(self, other):
        ret = AbstractResult.__cmp__(self, other)
        if ret != 0:
            return ret
        else:
            return compare_float(self.time_sec, other.time_sec)

    def __str__(self):
        i = self.input()
        return "%u %u %s %u %.1f" % (i.num_verts, i.num_edges, str(i.seed), self.run_num, self.time_sec)

    @staticmethod
    def header_row():
        return "#|V| |E| Seed Run# Time(sec)"

    @staticmethod
    def key(num_verts, num_edges, seed, run_num):
        return (Input(1, 0, 0.0, 1.0, num_verts, num_edges, seed), run_num)

    @staticmethod
    def from_list(lst):
        if(len(lst) != 5):
            raise DataError('PerfResult expected 5 args, got %u: %s' % (len(lst), str(lst)))
        return PerfResult(lst[0], lst[1], lst[2], lst[3], lst[4])

    @staticmethod
    def get_path_to(rev):
        return get_path_to_project_root() + 'result/perf/' + rev

class WeightResult(AbstractResult):
    """Data about an input, a revision, and the weight of the MST."""
    def __init__(self, dims, num_verts, seed, rev, run_num, mst_weight):
        AbstractResult.__init__(self, 15, dims, 0.0, 1.0, num_verts, num_verts*(num_verts-1)/2, seed, rev, run_num)
        self.mst_weight = float(mst_weight)

    def get_path(self):
        return self.get_path_to(self.input().get_wtype())

    def __cmp__(self, other):
        ret = AbstractResult.__cmp__(self, other)
        if ret != 0:
            return ret
        else:
            return compare_float(self.mst_weight, other.mst_weight)

    def __str__(self):
        i = self.input()
        return "%u %u %u %s %u %.15f" % (i.dims, i.num_verts, i.num_edges, str(i.seed), self.run_num, self.mst_weight)

    @staticmethod
    def header_row():
        return "#Dim |V| Seed Run#"

    @staticmethod
    def key(dims, num_verts, seed, run_num):
        return (Input(15, dims, 0.0, 1.0, num_verts, num_verts*(num_verts-1)/2, seed), run_num)

    @staticmethod
    def from_list(lst):
        if(len(lst) != 5):
            raise DataError('WeightResult expected 5 args, got %u: %s' % (len(lst), str(lst)))
        return WeightResult(lst[0], lst[1], lst[2], lst[3], lst[4])

    @staticmethod
    def get_path_to(wtype):
        return get_path_to_project_root() + 'result/weight/' + wtype

class ExtractInputFooterError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def __re_get_group(pattern, haystack, group_num=0):
    """Returns the value associated with the requested group num in the result
    from re.search, or raises an ExtractInputFooterError if it does not match"""
    x = re.search(pattern, haystack)
    if x is None:
        raise ExtractInputFooterError('pattern match failed for ' + pattern + ' in ' + haystack)
    else:
        return x.groups()[group_num]

def extract_input_footer(input_graph):
    """Returns the Input object representing the footer info"""
    lines = os.popen('tail -n 1 "%s" 2> /dev/null' % input_graph).readlines()
    if len(lines) == 0:
        raise ExtractInputFooterError("Failed to extract the footer from " + input_graph)
    about = lines[0]

    try:
        num_dims = int(__re_get_group(r' d=(\d*)', about))
    except ExtractInputFooterError:
        num_dims = 0

    num_verts = int(__re_get_group(r' m=(\d*)', about))
    num_edges = int(__re_get_group(r' n=(\d*)', about))
    min_val = float(__re_get_group(r' min=(\d*.\d*)', about))
    max_val = float(__re_get_group(r' max=(\d*.\d*)', about))
    precision = int(__re_get_group(r' prec=(\d*)', about))
    seed = int(__re_get_group(r' seed=(\d*)', about))
    return Input(precision, num_dims, min_val, max_val, num_verts, num_edges, seed)

def ppinput_fast(path):
    """Returns the path to an input_graph in 'printy-printed' string."""
    root_path = get_path_to_generated_inputs()
    n = len(root_path)
    if path[:n] == root_path:
        return path[n:]
    else:
        return path

def ppinput(path):
    """Returns the path to an input_graph in 'printy-printed' string."""
    if FAST_INPUT_PATH_PRETTY_PRINT:
        return ppinput_fast(path)
    else:
        try:
            inpt = extract_input_footer(path)
            return 'I(%s)' % inpt.make_args_for_generate_input()
        except ExtractInputFooterError:
            return ppinput_fast(path)

def get_tracked_revs():
    """Returns revisions we are tracking as an array of SHA1 revision IDs"""
    ret = []
    try:
        fh = open(get_path_to_tools_root() + 'conf/tracked_revs', "r")
        lines = fh.readlines()
        for line in lines:
            if line[0:1] != '#':
                s = line.split('\t', 4)
                if len(s) != 4:
                    raise DataError('line should have four columns (has %d): %s' % (len(s), line))
                ret.append(s[2])
        fh.close()
        return ret
    except IOError, e:
        raise DataError('I/O error while reading tracked revisions: ' + e)
