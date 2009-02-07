#!/usr/bin/env python

from mstutil import get_path_to_tools_root, get_tracked_inputs, get_tracked_revs
from mstutil import get_correctness_results, get_performance_results, get_weight_results
from optparse import OptionGroup, OptionParser
import os, sys

def get_num_runs_missing_for_data(data, input_graph, num_desired_runs):
    """Returns the number of values left to be collected."""
    input_graph = os.path.basename(input_graph)
    if data.has_key(input_graph):
        return max(0, num_desired_runs - len(data[input_graph]))
    else:
        return num_desired_runs

def collect_missing_correctness_data(input_graph, rev, _):
    cmd = 'run_test.py -i %s -r %s -n 1 -c -q -x' % (input_graph, rev)
    return os.system(get_path_to_tools_root() + cmd) == 0

def collect_missing_performance_data(input_graph, rev, num_runs):
    cmd = 'run_test.py -i %s -r %s -n %s -q' % (input_graph, rev, num_runs)
    return os.system(get_path_to_tools_root() + cmd) == 0

def collect_missing_weight_data(inputs, rev, num_runs):
    (wtype, num_verts) = inputs
    cmd = 'run_test.py -g %s,%s -r %s -n %s -q' % (num_verts, wtype, rev, num_runs)
    return os.system(get_path_to_tools_root() + cmd) == 0

def main():
    usage = """usage: %prog [options]
Searches for missing results and uses run_test.py to collect it."""
    parser = OptionParser(usage)
    parser.add_option("-i", "--input_graph",
                      metavar="FILE",
                      help="restrict the missing data check to the specified input graph")
    parser.add_option("-l", "--list-only",
                      action="store_true", default=False,
                      help="only list missing data (do not collect it)")
    parser.add_option("-n", "--num-runs",
                      type="int", default="5",
                      help="number of desired runs per revision-input combination [default: %default]")
    parser.add_option("-r", "--rev",
                      help="restrict the missing data check to the specified revision")

    group = OptionGroup(parser, "Data Collection Options")
    group.add_option("-p", "--performance",
                      action="store_true", default=True,
                      help="collect performance data (this is the default)")
    group.add_option("-c", "--correctness",
                      action="store_true", default=False,
                      help="collect correctness data")
    group.add_option("-v", "--num_vertices",
                      metavar="V", type="int", default=0,
                      help="collect weight data for V vertices (requires -d or -e)")
    group.add_option("-d", "--dimensionality",
                      metavar="D", type="int", default=0,
                      help="collect weight data for randomly positioned vertices in D-dimensional space (requires -v)")
    group.add_option("-e", "--edge",
                      action="store_true", default=False,
                      help="collect weight data for random uniform edge weights in the range (0, 1] (requires -v)")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.error("too many arguments")

    if options.num_runs < 1:
        parser.error("-n must be at least 1")

    # prepare for a weight data collection
    num_on = 0
    if options.num_vertices > 0:
        if options.input_graph:
            parser.error('-i and -v are mutually exclusive')

        if options.dimensionality > 0:
            num_on += 1
            wtype = 'loc%u' % options.dimensionality

        if options.edge:
            num_on += 1
            wtype = 'edge'

        if num_on == 0:
            parser.error('-v requires either -d or -e be specified too')

        inputs = (wtype, options.num_vertices)
        get_results = (lambda _ : get_weight_results(wtype))
        collect_missing_data = collect_missing_weight_data

    # prepare for a correctness data collection
    if options.correctness:
        num_on += 1
        get_results = lambda rev : get_correctness_results(rev)
        collect_missing_data = collect_missing_correctness_data
        if options.num_runs > 1:
            options.num_runs = 1
            print 'warning: number of runs coerced to 1 for correctness checking'

    # make sure no more than 1 type of data collection was specified
    if num_on > 1:
        parser.error('at most one of -c, -d, and -e may be specified')
    elif num_on == 0:
        # prepare for a performance data collection (default if nothing else is specified)
        get_results = lambda rev : get_performance_results(rev)
        collect_missing_data = collect_missing_performance_data

    # prepare the inputs for non-weight data collection schemes
    if options.num_vertices == 0:
        if options.input_graph is not None:
            inputs = [options.input_graph]
        else:
            inputs = get_tracked_inputs()

    # prepare the revisions to collect data for
    if options.rev is not None:
        revs = [options.rev]
    else:
        revs = get_tracked_revs()

    # collect the data
    missing_none = True
    for rev in revs:
        data = get_results(rev)
        for i in inputs:
            n = get_num_runs_missing_for_data(data, i, options.num_runs)
            if n > 0:
                msg = None
                if options.list_only:
                    missing_none = False
                    msg = 'missing'
                elif not collect_missing_data(i, rev, n):
                    missing_none = False
                    msg = 'failed to collect'
                if msg is not None:
                    print '%s: input=%s \t rev=%s runsLeft=%u' % (msg, i, rev, n)

    if missing_none:
        print 'No performance data is missing!'

if __name__ == "__main__":
    sys.exit(main())
