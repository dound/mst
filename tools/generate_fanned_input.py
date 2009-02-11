#!/usr/bin/env python

from generate_input import main as generate_input, edges_in_complete_undirected_graph
from optparse import OptionParser
import sys

def get_edges_from_density(num_verts, density):
    min_edges = num_verts - 1
    max_edges = edges_in_complete_undirected_graph(num_verts)
    return int((1.0-density)*min_edges + density*max_edges)

def main(argv=sys.argv[1:]):
    usage = """usage: %prog [options] NUM_VERTICES
Uses generate_input.py to generate a variety of edge densities for a given
number of vertices.  The edge densities used will be the maximum edge density
(-m) down to 0.0 (excluded unless -z is specified) in steps of -d.

Example: Generate 5 inputs and log them to the corr.inputs file with correctness
         values for 10 vertices and for densities 1.0, 0.75, 0.5, and 0.25:
         %prog -n5 -g '-l ../input/corr.inputs -c' 10"""
    parser = OptionParser(usage)
    parser.add_option("-d", "--density-interval",
                      type="float", default=0.25, metavar="D",
                      help="spacing between inputs in terms of the edge density interval [default: %default]")
    parser.add_option("-g", "--generate-input",
                      metavar="GEN_ARGS", default="",
                      help="extra arguments to pass to generate_input.py")
    parser.add_option("-m", "--max-density",
                      type="float", default=1.0, metavar="D",
                      help="maximum edge density [default: %default]")
    parser.add_option("-n", "--num-runs-per-edge-density",
                      type="int", default=1, metavar="n",
                      help="number of inputs to generate for each edge density [default: %default]")
    parser.add_option("-z", "--zero",
                      action="store_true", default=False,
                      help="generate zero-density (spanning tree) graphs too")

    (options, args) = parser.parse_args(argv)
    if len(args) < 1:
        parser.error("missing NUM_VERTICES")
    elif len(args) > 1:
        parser.error("too many arguments")
    try:
        v = int(args[0])
        if v <= 0:
            parser.error('NUM_VERTICES must be at least 1')
    except ValueError:
        parser.error('NUM_VERTICES must be an integer')

    di = options.density_interval
    if di < 0.0 or di > 1.0:
        parser.error('-d must be between 0 and 1 inclusive')

    n = options.num_runs_per_edge_density
    if n < 0:
        parser.error('-n must be greater than or equal to 0')

    d = options.max_density
    if d < 0.0 or d > 1.0:
        parser.error('-d must be between 0 and 1 inclusive')

    extra_args = options.generate_input
    while d >= 0.0:
        if d == 0 and not options.zero:
            break

        e = get_edges_from_density(v, d)
        for _ in range(n):
            args = ('-n %u %s %u' % (e, extra_args, v)).split()
            try:
                ret = generate_input(args)
            except Exception, errstr:
                print >> sys.stderr, 'fan_gen failed: ' + errstr
                return -1
            if ret != 0:
                print >> sys.stderr, 'fan_gen failed'
                return -1
        d -= di

    return 0

if __name__ == "__main__":
    sys.exit(main())
