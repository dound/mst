#!/usr/bin/env python

from generate_input import main as generate_input, edges_in_complete_undirected_graph
from mstutil import get_path_to_project_root
from optparse import OptionParser
import sys

def main(argv=sys.argv[1:]):
    usage = """usage: %prog [options] NUM_VERTICES
Generates input for evaluating performance at different edge densities for a given |V|."""
    parser = OptionParser(usage)
    parser.add_option("-a", "--additive-step-type",
                      action="store_true", default=False,
                      help="use additive stepping between numbers of vertices [default: multiplicative]")
    parser.add_option("-l", "--min",
                      type="float", default=4.0,
                      help="minimum edge:vertex ratio to generate a graph for [default: %default]")
    parser.add_option("-n", "--num-per-step",
                      type="int", default=1, metavar="n",
                      help="number of inputs to generate for each step [default: %default]")
    parser.add_option("-s", "--step",
                      type="float", default=2.0,
                      help="step amount between edge:vertex ratios (see -a) [default: %default]")
    parser.add_option("-u", "--max",
                      type="float", default=1500.0,
                      help="maximum edge:vertex ratio to generate a graph for [default: %default]")
    (options, args) = parser.parse_args(argv)
    if len(args) < 1:
        parser.error("missing NUM_VERTICES")
    elif len(args) > 1:
        parser.error("too many arguments")

    try:
        num_verts = int(args[0])
        inputs_list_file = get_path_to_project_root() + 'input/density-%u.inputs' % num_verts
    except ValueError:
        parser.error('NUM_NUM_VERTSERTICES must be a positive integer')
    if num_verts < 1:
        parser.error('NUM_VERTICES must be at least 1')

    if options.min < 1 or options.min > options.max:
        parser.error('-l must be in the range [1, max]')

    max_edges = edges_in_complete_undirected_graph(num_verts)
    max_ratio = max_edges / num_verts
    if options.max < 1:
        parser.error('-u must be at least 1')
    elif options.max > max_ratio:
        fmt = 'max edge:vertex ratio for %u vertices is %.1f, but -u specified a ratio of %u'
        parser.error(fmt % (num_verts, max_ratio, options.max))

    if options.additive_step_type:
        if options.step < 1.0:
            parser.error('-s must be greater than or equal to 1 when -a is used')
    elif options.step <= 1.0:
        parser.error('-s must be greater than 1 when -a is not used')

    d = options.min
    while True:
        for _ in range(options.num_per_step):
            num_edges = int(d * num_verts)
            if num_edges > max_edges:
                num_edges = max_edges
            args = '-p1 -l %s -n %u %u' % (inputs_list_file, num_edges, num_verts)
            try:
                print 'generating new input: ' + args
                ret = generate_input(args.split())
            except Exception, errstr:
                print >> sys.stderr, 'generate_density_inputs failed for: ' + args + ': ' + str(errstr)
                return -1
            if ret != 0:
                print >> sys.stderr, 'generate_density_inputs failed for: ' + args
                return -1

        if d >= options.max:
            break
        if options.additive_step_type:
            d += options.step
        else:
            d *= options.step
        if d > options.max:
            d = options.max

    return 0

if __name__ == "__main__":
    sys.exit(main())
