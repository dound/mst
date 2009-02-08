#!/usr/bin/env python

from math import sqrt
from mstutil import die, get_path_to_inputs
from optparse import OptionParser
from os import urandom
from random import Random
from struct import unpack
from time import strftime
import heapq, sys

__RND_SEED = unpack('Q', urandom(8))[0]  # generate a truly random 8-byte seed
__rnd = Random(__RND_SEED)

def print_input_header(num_verts, num_edges, about, out):
    min_edges = num_verts - 1
    num_edges_scaled = num_edges - min_edges
    num_edge_choices = edges_in_complete_undirected_graph(num_verts) - min_edges
    density = float(num_edges_scaled) / num_edge_choices

    # stick a comment in the input file describing it
    print >> out, '# %s: %s density=%.2f' % (strftime('%A %Y-%b-%d at %H:%M:%S'), about, density)

    # the real header
    print >> out, '%u\n' % num_verts
    print >> out, '%u\n' % num_edges

def edges_in_complete_undirected_graph(num_verts):
    return (num_verts * (num_verts - 1)) / 2

def gen_random_edge_lengths(num_verts, num_edges, min_edge_len, max_edge_len, precision, out):
    # print the header for the graph file being generated
    about = "m=%d n=%d min=%.1f max=%.1f prec=%d seed=%s" % (num_verts, num_edges,
                                                             min_edge_len, max_edge_len, precision, str(__RND_SEED))
    print_input_header(num_verts, num_edges, about, out)
    fmt = '%u %u %.' + str(precision) + 'f'

    # handle the complete graph case efficiently
    if edges_in_complete_undirected_graph(num_verts) == num_edges:
        for i in range(0, num_verts):
            for j in range(i+1, num_verts):
                print >> out, fmt % (i, j, __rnd.uniform(min_edge_len, max_edge_len))
        return

    # handle the non-complete graph case: O(|V|^2 * log(|V|^2))

    # a hashtable to remember which nodes form a spannning tree (ST): contains
    # tuple (u,v) if it is part of our ST
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
        return

    # 2) randomly add any remaining edges between unconnected vertices
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

def gen_random_vertex_positions(num_verts, num_edges, num_dims, min_pos, max_pos, precision, out):
    if edges_in_complete_undirected_graph(num_verts) != num_edges:
        die('not yet implemented error: gen_random_vertex_positions only works for generating complete graphs')

    # generate all of the coordinates in one big array
    coords = [__rnd.uniform(min_pos,max_pos) for _ in range(num_verts*num_dims)]

    # print the header for the graph file being generated
    about = "m=%d n=%d d=%d min=%.1f max=%.1f prec=%d seed=%s" % (num_verts, num_edges, num_dims,
                                                                  min_pos, max_pos, precision, str(__RND_SEED))
    print_input_header(num_verts, num_edges, about, out)

    # print the edge weights for each pair
    fmt = '%u %u %.' + str(precision) + 'f'
    for i in range(0, num_verts):
        io = i * num_dims
        for j in range(i+1, num_verts):
            jo = j * num_dims
            print >> out, fmt % (i, j, sqrt(sum([(coords[io+o]-coords[jo+o])*(coords[io+o]-coords[jo+o]) for o in range(num_dims)])))

def main():
    usage = """usage: %prog [options] NUM_VERTICES
Generates a connected graph with no self-loops or parallel edges.  Output is
sent to the default filename unless -e or -v is specified: in these cases, -o
must be specified."""

    parser = OptionParser(usage)
    parser.add_option("-n", "--num-edges",
                      help="number of edges to put in the graph [default: complete graph]")
    parser.add_option("-o", "--output-file",
                      help="where to output the generated graph [default is inputs/<STYLE>-<NUM_VERTICES>-<NUM_EDGES>-<RANDOM_SEED>.g")
    parser.add_option("-p", "--precision",
                      type="int", default=1,
                      help="number of decimal points to specify for edge weights [default: %default]")
    parser.add_option("-e", "--edge-weight-range",
                      metavar="MIN,MAX",
                      help="range of edge weights (range inclusive) [default: [0.1,100000]]")
    parser.add_option("-v", "--vertex-pos-range",
                      metavar="DIM,MIN,MAX",
                      help="dimensionality of vertex positions and the range of each dimension (range inclusive) [not used by default; mutually exclusive with -e]")
    parser.add_option("-s", "--style",
                      help="how to place edges [default: random with no self-loops or parallel edges]")

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("missing NUM_VERTICES")
    elif len(args) > 1:
        parser.error("too many arguments")

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
        if options.vertex_pos_range or options.edge_weight_range:
            parser.error('-e or -v require -o to be specified too')
        else:
            options.output_file = get_path_to_inputs() + '%s%u-%u-%s.g' % (style_str, num_verts, num_edges, str(__RND_SEED))

    # open the desired output file
    if options.output_file == 'stdout':
        out = sys.stdout
    else:
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

        gen_random_vertex_positions(num_verts, num_edges, num_dims, min_pos, max_pos, options.precision, out)
        return

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

    gen_random_edge_lengths(num_verts, num_edges, min_edge_len, max_edge_len, options.precision, out)
    if out != sys.stdout:
        out.close()

if __name__ == "__main__":
    sys.exit(main())
