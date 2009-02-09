from mstutil import die, get_path_to_inputs

class TrackedInput:
    """Data about about how to generate an input, and optionally the MST weight of that input."""
    def __init__(self, prec, dim, min_val, max_val, num_verts, num_edges, seed, mst_weight='-1'):
        self.precision = int(prec)
        self.dimensionality = int(dim)
        self.min = float(min_val)
        self.max = float(max_val)
        self.num_verts = int(num_verts)
        self.num_edges = int(num_edges)
        self.seed = int(seed)
        self.mst_weight = float(mst_weight)

    def update_mst_weight(self, v):
        """Updates the mst_weight field if v is non-negative"""
        if self.mst_weight < 0 or v >= 0:
            self.mst_weight = v

    def __cmp__(self, other):
        """Provides some ordering on TrackedInput - ignores mst_weight field."""
        if self.precision != other.precision:
            return self.precision - other.precision
        if self.dimensionality != other.dimensionality:
            return self.dimensionality - other.dimensionality
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
        if self.seed != other.seed:
            return self.seed - other.seed
        return 0

    def __hash__(self):
        """Simple hash on vertices, edges, and the seed"""
        ret = self.num_verts
        ret = ret * 31 + self.num_edges
        return ret * 31 + self.seed

    def __str__(self):
        return "%s %u %s %s %u %u %s %s" % (str(self.precision), self.dimensionality, str(self.min), str(self.max),
                                            self.num_verts, self.num_edges, str(self.seed), str(self.mst_weight))

def get_tracked_input_fn(precision, dimensionality, min_val, max_val):
    """Returns the log file which has results of the specified type"""
    may_be_part2_input = (precision==15 and min_val==0 and max_val==1)
    if dimensionality == 0:
        if precision==1 and min_val==0 and max_val==100000:
            logbasename = 'perf.inputs'
        elif may_be_part2_input:
            logbasename = 'p2-redge.inputs'
        else:
            logbasename = 'other-redge.inputs'
    else:
        if may_be_part2_input:
            logbasename = 'p2-rvert-%ud.inputs' % dimensionality
        else:
            logbasename = 'other-rvert.inputs'
    return get_path_to_inputs() + logbasename

def get_tracked_inputs(logfn):
    """Returns in a dictionary the list of inputs from an input log file"""
    inputs = {}
    fh = None
    try:
        fh = open(logfn, "r")
        lines = fh.readlines()
        for line in lines:
            s = line.split()
            if len(s) != 8:
                die("Error in %s: rows should have 8 values: precision dimensionality min_val max_val |V| |E| seed mst_weight" % logfn)
            t = TrackedInput(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7])
            inputs[t] = t
    except IOError, errstr:
        die("I/O reading tracked inputs in %s: %s" % (logfn, errstr))
    except ValueError, errstr:
        die("Improper value encountered when reading tracked inputs in %s: %s" % (logfn, errstr))
    finally:
        if fh is not None:
            fh.close()
    return inputs

def save_tracked_inputs(logfn, inputs):
    """Save inputs to the specified log file"""
    tracked_inputs = sorted(inputs.keys())
    fh = None
    try:
        fh = open(logfn, "w")
        for t in tracked_inputs:
            fh.write('%s\n' % str(t))
    except IOError, errstr:
        die("I/O reading tracked inputs in %s: %s" % (logfn, errstr))
    finally:
        if fh is not None:
            fh.close()

def track_input(precision, dimensionality, min_val, max_val, num_verts, num_edges, seed, mst_weight='-1'):
    """Adds an entry to the appropriate input log about this entry (if the entry
    already exists, it is simply updated).

    @param dimensionality 0=>random edge weights; otherwise it indicates the dim of
    the space in which vertices are randomly located
    """
    logfn = get_tracked_input_fn(precision, dimensionality, min_val, max_val)
    inputs = get_tracked_inputs(logfn)
    t = TrackedInput(precision, dimensionality, min_val, max_val, num_verts, num_edges, seed, mst_weight)
    if inputs.has_key(t):  # matches on everything except mst_weight
        t_old = inputs[t]
        changed = t_old.update_mst_weight(mst_weight)
    else:
        inputs[t] = t
        changed = True
    if changed:
        save_tracked_inputs(logfn, inputs)
