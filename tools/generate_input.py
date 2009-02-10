#!/usr/bin/env python

from check_output import CheckerError, compute_mst_weight
from input_tracking import track_input, TrackedInput
from math import sqrt
from mstutil import die, get_path_to_generated_inputs
from optparse import OptionGroup, OptionParser
from os import urandom
from random import Random
from struct import unpack
from time import strftime
import heapq, os, re, sys

__RND_SEED = None
__rnd = None

def print_input_header(num_verts, num_edges, out):
    print >> out, '%u' % num_verts
    print >> out, '%u' % num_edges

def print_input_footer(num_verts, num_edges, about, out):
    """End with a comment in the input file describing it.  It should not be
    read by mst since it doesn't expect lines after the last edge."""
    min_edges = num_verts - 1
    num_edges_scaled = num_edges - min_edges
    num_edge_choices = edges_in_complete_undirected_graph(num_verts) - min_edges
    density = float(num_edges_scaled) / num_edge_choices
    print >> out, '# %s: %s density=%.2f' % (strftime('%A %Y-%b-%d at %H:%M:%S'), about, density)

class ExtractInputFooterError:
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def __re_get_group(pattern, haystack, group_num=0):
    """Returns the value associated with the requested group num in the result
    from re.search, or raises an ExtractInputFooterError if it does not match"""
    x = re.search(pattern, haystack)
    if x is None:
        return None
    else:
        return x.groups()[group_num]

def extract_input_footer(input_graph):
    """Returns the TrackedInput representing the footer info"""
    lines = os.popen('tail -n 1 "%s" 2> /dev/null' % input_graph).readlines()
    if len(lines) == 0:
        raise ExtractInputFooterError("Failed to extract the footer from " + input_graph)
    about = lines[0]

    try:
        num_dims = int(__re_get_group(r'd=(\d*)', about))
    except ExtractInputFooterError:
        num_dims = 0

    num_verts = int(__re_get_group(r'm=(\d*)', about))
    num_edges = int(__re_get_group(r'n=(\d*)', about))
    min_val = float(__re_get_group(r'min=(\d*.\d*)', about))
    max_val = float(__re_get_group(r'max=(\d*.\d*)', about))
    precision = int(__re_get_group(r'prec=(\d*)', about))
    seed = int(__re_get_group(r'seed=(\d*)', about))
    return TrackedInput(precision, num_dims, min_val, max_val, num_verts, num_edges, seed)

def edges_in_complete_undirected_graph(num_verts):
    return (num_verts * (num_verts - 1)) / 2

def gen_random_edge_lengths(num_verts, num_edges, min_edge_len, max_edge_len, precision, out):
    about = "m=%d n=%d min=%.1f max=%.1f prec=%d seed=%s" % (num_verts, num_edges,
                                                             min_edge_len, max_edge_len, precision, str(__RND_SEED))
    print_input_header(num_verts, num_edges, out)
    fmt = '%u %u %.' + str(precision) + 'f'

    # handle the complete graph case efficiently
    if edges_in_complete_undirected_graph(num_verts) == num_edges:
        for i in range(0, num_verts):
            for j in range(i+1, num_verts):
                print >> out, fmt % (i, j, __rnd.uniform(min_edge_len, max_edge_len))
        return about

    # handle the non-complete graph case

    # a hashtable to remember which nodes form a spannning tree (ST): contains
    # tuple (u,v) if it is part of our ST (only use u > v: links are unidir)
    spanning_tree = {}

    # 1) make sure we end up with a connected graph by walking through each node
    #    and randomly connecting it to one of the previous nodes
    for i in range(1,num_verts):  # skip first vertex
        # pick a random vertex in the connected part of the graph to connect to
        j = __rnd.randint(0, i-1)
        spanning_tree[(i,j)] = True
        print >> out, fmt % (i, j, __rnd.uniform(min_edge_len, max_edge_len))

    # account for the edges we just added
    num_edges -= (num_verts - 1)
    if num_edges == 0:
        return about

    # 2) randomly add any remaining edges between unconnected vertices

    # We have two algorithms - one specialized for dense matrices, the other for
    # sparse matrices.  The running times are (let Z = (V * (V - 1)):
    #     dense:  Z * log(Z) + E * log(Z) = O(V^2*log(V^2))
    #     sparse: E * Z / (Z - 2 * E)     = O(E*V^2 / (V^2 - E))
    #
    # Empirically, sparse is faster than dense unless the density is less
    # than about 0.5.
    #
    # However, the above estimate for sparse is actually a bit loose - it
    # assumes every edge is as hard to insert as the last edge being inserted.
    # The tight upper bound would be:
    #     sparse: sum from i=0 to i=E-1 (inclusive) over 1 / prob_success
    #             prob_success = 1 - 2 * i / (V^2 - V)
    #
    # I do not know how to reduce this summation so we can compare it with the
    # dense algorithm, but empirically it is this tight bound for sparse is
    # faster that the dense algorithm for all densities.

    # Assume the loose upper-bound is correct and switch over to the dense
    # algorithm when the density is quite high (empirically measured).
    density = num_edges / float(edges_in_complete_undirected_graph(num_verts))
    print 'density=%s' % str(density)
    if density > 0.5 and False:
        print 'here'
        heap = []

        # put all edges in the heap with some random key
        for i in range(0, num_verts):
            for j in range(i+1, num_verts):
                heapq.heappush(heap, (__rnd.random(), i, j))

        # use the minimum edges in the heap as the edges in our graph
        while num_edges > 0:
            (_, i, j) = heapq.heappop(heap)
            if not spanning_tree.has_key((i, j)):
                num_edges -= 1
                print >> out, fmt % (i, j, __rnd.uniform(min_edge_len, max_edge_len))
    else:
        while num_edges > 0:
            # choose random vertices for an edge to connect
            r1 = __rnd.randint(0, num_verts)
            r2 = __rnd.randint(0, num_verts)
            if r1 > r2:
                i = r1
                j = r2
            else:
                i = r2
                j = r1
            # add the edge if it is new
            if i!=j and not spanning_tree.has_key((i, j)):
                spanning_tree[(i, j)] = True
                print >> out, fmt % (i, j, __rnd.uniform(min_edge_len, max_edge_len))
                num_edges -= 1

    return about

def gen_random_vertex_positions(num_verts, num_edges, num_dims, min_pos, max_pos, precision, out):
    if edges_in_complete_undirected_graph(num_verts) != num_edges:
        die('not yet implemented error: gen_random_vertex_positions only works for generating complete graphs')

    # generate all of the coordinates in one big array
    coords = [__rnd.uniform(min_pos,max_pos) for _ in range(num_verts*num_dims)]

    print_input_header(num_verts, num_edges, out)

    # print the edge weights for each pair
    fmt = '%u %u %.' + str(precision) + 'f'
    for i in range(0, num_verts):
        io = i * num_dims
        for j in range(i+1, num_verts):
            jo = j * num_dims
            print >> out, fmt % (i, j, sqrt(sum([(coords[io+o]-coords[jo+o])*(coords[io+o]-coords[jo+o]) for o in range(num_dims)])))

    return "m=%d n=%d d=%d min=%.1f max=%.1f prec=%d seed=%s" % (num_verts, num_edges, num_dims,
                                                                 min_pos, max_pos, precision, str(__RND_SEED))

def main(argv=sys.argv[1:]):
    usage = """usage: %prog [options] NUM_VERTICES
Generates a connected graph with no self-loops or parallel edges.  Output is
sent to the default filename (""" + get_path_to_generated_inputs() + """/with
V-E-SEED.g unless -e or -v are specified in which case a random filename is
used.)"""
    parser = OptionParser(usage)
    parser.add_option("-c", "--correctness",
                      action="store_true", default=False,
                      help="compute and log the correct output")
    parser.add_option("-m", "--may-use-existing",
                      action="store_true", default=False,
                      help="will not generate a new graph if the output file already exists")
    parser.add_option("-n", "--num-edges",
                      help="number of edges to put in the graph [default: complete graph]")
    parser.add_option("-o", "--output-file",
                      help="where to output the generated graph [default is inputs/[<STYLE>-]<NUM_VERTICES>-<NUM_EDGES>-<RANDOM_SEED>.g")
    parser.add_option("-p", "--precision",
                      type="int", default=1,
                      help="number of decimal points to specify for edge weights [default: %default]")
    parser.add_option("-q", "--quiet",
                      action="store_true", default=False,
                      help="do not log any extraneous information to stdout")
    parser.add_option("-r", "--random-seed",
                      metavar="R", type="int", default=None,
                      help="what random seed to use [default: choose a truly random seed using urandom()]")
    parser.add_option("-s", "--style",
                      help="how to place edges [default: random with no self-loops or parallel edges]")
    parser.add_option("-t", "--dont-track",
                      action="store_true", default=False,
                      help="whether to log this input in our list of generated inputs")

    group = OptionGroup(parser, "Generation Type Options")
    group.add_option("-e", "--edge-weight-range",
                     metavar="MIN,MAX",
                     help="range of edge weights (range inclusive) [default: [0.1,100000]]")
    group.add_option("-v", "--vertex-pos-range",
                     metavar="DIM,MIN,MAX",
                     help="dimensionality of vertex positions and the range of each dimension (range inclusive) [not used by default; mutually exclusive with -e]")
    parser.add_option_group(group)

    (options, args) = parser.parse_args(argv)
    if len(args) < 1:
        parser.error("missing NUM_VERTICES")
    elif len(args) > 1:
        parser.error("too many arguments")

    # initialize the random number generator
    global __RND_SEED
    global __rnd
    if options.random_seed is not None:
        __RND_SEED = options.random_seed
    else:
        __RND_SEED = unpack('Q', urandom(8))[0]  # generate a truly random 8-byte seed
    __rnd = Random(__RND_SEED)

    def print_if_not_quiet(msg):
        if not options.quiet:
            print msg

    # determine how many vertices should be in the graph
    try:
        num_verts = int(args[0])
    except ValueError:
        parser.error("NUM_VERTICES must be an integer")

    try:
        sne = options.num_edges
        if sne == 'c' or sne == 'complete' or sne is None:
            num_edges = edges_in_complete_undirected_graph(num_verts)
        else:
            num_edges = int(sne)
            if num_edges > edges_in_complete_undirected_graph(num_verts):
                parser.error("-n may not be larger than NUM_VERTICES*(NUM_VERTICES-1)/2 (complete graph may not have self-loops or parallel edges)")
            elif num_edges < num_verts - 1:
                parser.error("-n may not be less than NUM_VERTICES-1 (graph must be connected)")
    except ValueError:
        parser.error("-n must either be an integer or 'complete'")

    if options.precision <= 0:
        parser.error("-p must be at least 1")
    elif options.precision > 15:
        parser.error("-p must be no more than 15 (doubles cannot accurately represent more than this)")

    if options.style is not None:
        parser.error("option -s is not yet supported")
    else:
        style_str = ''

    if options.edge_weight_range and options.vertex_pos_range:
        parser.error("option -e and -v are mutually exclusive")

    # determine the output file to use
    if options.output_file is None:
        path = get_path_to_generated_inputs()
        if options.vertex_pos_range or options.edge_weight_range:
            options.output_file = path + 'other-' + str(__RND_SEED) + '.g'
        else:
            options.output_file = path + '%s%u-%u-%s.g' % (style_str, num_verts, num_edges, str(__RND_SEED))

    # open the desired output file
    if options.output_file == 'stdout':
        out = sys.stdout
    else:
        if options.may_use_existing and os.path.exists(options.output_file):
            print_if_not_quiet('skipping input generation: %s already exists' % options.output_file)
            return 0
        try:
            out = open(options.output_file, 'w')
        except IOError, errstr:
            die('generate_input: error: ' + errstr)

    # see if the user wants edge weights computed from vertex positions
    if options.vertex_pos_range:
        (d, m1, m2) = options.vertex_pos_range.split(',', 3)
        try:
            (num_dims, min_pos, max_pos) = (int(d), float(m1), float(m2))
        except ValueError:
            parser.error("option -v requires its arguments to be in the form int,float,float")

        if num_dims < 0:
            parser.error("option -v requires dimensionality to be a strictly positive integer")

        about = gen_random_vertex_positions(num_verts, num_edges, num_dims, min_pos, max_pos, options.precision, out)
        dimensionality = num_dims
        min_val = min_pos
        max_val = max_pos
    else:
        # default: randomly choose edge weights in some range
        if options.edge_weight_range:
            (m1, m2) = options.edge_weight_range.split(',', 2)
            try:
                (min_edge_len, max_edge_len) = (float(m1), float(m2))
            except ValueError:
                parser.error("option -e requires its arguments to be in the form float,float")

            if min_edge_len < 0.0:
                parser.error("option -e requires minimum edge length to be >= 0.0")
            if min_edge_len > max_edge_len:
                parser.error("option -e requires the minimum edge length < maximum edge length")
        else:
            # use defaults which describes the maximum range for the assignment
            min_edge_len = 0
            max_edge_len = 100000

        about = gen_random_edge_lengths(num_verts, num_edges, min_edge_len, max_edge_len, options.precision, out)
        dimensionality = 0
        min_val = min_edge_len
        max_val = max_edge_len

    print_input_footer(num_verts, num_edges, about, out)
    print_if_not_quiet('graph saved to ' + options.output_file)
    if out != sys.stdout:
        out.close()

    # generate output with correctness checker, if desired
    mst_weight = -1
    if options.correctness:
        if options.dont_track:
            print >> sys.stderr, "warning: skipping correctness output (only done when -t is not specified)"
            return 0
        try:
            mst_weight = compute_mst_weight(options.output_file, "correctness")
        except CheckerError, e:
            print >> sys.stderr, e

    # record this new input in our input log
    if not options.dont_track:
        logfn = track_input(options.precision, dimensionality, min_val, max_val, num_verts, num_edges, __RND_SEED, mst_weight)
        print_if_not_quiet('logged to ' + logfn)

    return 0

if __name__ == "__main__":
    sys.exit(main())
