#!/usr/bin/env python

from data import DataError, DataSet, InputSolution, CorrResult, PerfResult, WeightResult, get_tracked_revs
from data import extract_input_footer, ExtractInputFooterError
from mstutil import get_path_to_project_root, get_path_to_tools_root

from optparse import OptionGroup, OptionParser
import os, sys

def get_num_runs_missing_for_data(results, inpt, num_desired_runs):
    """Returns the number of values left to be collected."""
    for i in range(num_desired_runs):
        key = (inpt, i)
        if not results.has_key(key):
            return num_desired_runs - i
    return 0

def collect_missing_correctness_data(inpt, rev, first_run_id, num_runs, inputs_list_file_arg):
    # use a for-loop here b/c run_test only does -c on the first run it is called
    gen = inpt.make_args_for_generate_input() + ' --may-use-existing'
    for _ in range(num_runs):
        cmd = 'run_test.py -g "%s" -r %s -n 1 -c -x -t %u%s' % (gen, rev, first_run_id+1, inputs_list_file_arg)
    ret = os.system(get_path_to_tools_root() + cmd)
    return ret == 0

def collect_missing_performance_data(inpt, rev, first_run_id, num_runs):
    gen = inpt.make_args_for_generate_input() + ' --may-use-existing'
    cmd = 'run_test.py -g "%s" -r %s -n %u -t %u' % (gen, rev, num_runs, first_run_id)
    ret = os.system(get_path_to_tools_root() + cmd)
    return ret == 0

def collect_missing_weight_data(inpt, _, first_run_id, num_runs):
    gen = inpt.make_args_for_generate_input() + ' --may-use-existing'
    cmd = 'run_test.py -g "%s" -n %u -t %u' % (gen, num_runs, first_run_id)
    ret = os.system(get_path_to_tools_root() + cmd)
    return ret == 0

def main():
    usage = """usage: %prog [options]
Searches for missing results and uses run_test.py to collect it."""
    parser = OptionParser(usage)
    parser.add_option("-i", "--input_graph",
                      metavar="FILE",
                      help="restrict the missing data check to the specified input graph")
    parser.add_option("-l", "--inputs-list-file",
                      metavar="FILE",
                      help="collect data for all inputs in the specified log file")
    parser.add_option("--list-only",
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
    parser.add_option_group(group)

    group2 = OptionGroup(parser, "Weight (Part II) Data Collection Options")
    group2.add_option("-v", "--num_vertices",
                      metavar="V", type="int", default=0,
                      help="collect weight data for V vertices (requires -d or -e)")
    group2.add_option("-d", "--dims",
                      metavar="D", type="int", default=0,
                      help="collect weight data for randomly positioned vertices in D-dimensional space (requires -v)")
    group2.add_option("-e", "--edge",
                      action="store_true", default=False,
                      help="collect weight data for random uniform edge weights in the range (0, 1] (requires -v)")
    parser.add_option_group(group2)

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.error("too many arguments")

    if options.num_runs < 1:
        parser.error("-n must be at least 1")
    input_solns = None

    # prepare for a weight data collection
    num_on = 0
    if options.num_vertices > 0:
        if options.input_graph or options.inputs_list_file:
            parser.error('-i, -l, and -v are mutually exclusive')

        if options.dims > 0:
            num_on += 1
            wtype = 'loc%u' % options.dims

        if options.edge:
            num_on += 1
            wtype = 'edge'

        if num_on == 0:
            parser.error('-v requires either -d or -e be specified too')

        input_path = InputSolution.get_path_to(15, options.dims, 0.0, 1.0)
        input_solns = DataSet.read_from_file(InputSolution, input_path)
        revs = [None] # not revision-specific (assuming our alg is correct)
        get_results_for_rev = lambda _ : DataSet.read_from_file(WeightResult, WeightResult.get_path_to(wtype))
        collect_missing_data = collect_missing_weight_data
    elif options.dims > 0 or options.edge:
        parser.error('-v is required whenever -d or -e is used')

    # handle -i, -l: collect data for a particular graph(s)
    if options.input_graph and options.inputs_list_file:
        parser.error('-i and -l are mutually exclusive')
    if options.input_graph is not None:
        try:
            i = extract_input_footer(options.input_graph)
        except ExtractInputFooterError, e:
            parser.error(e)
        input_solns = DataSet({0:InputSolution(i.prec,i.dims,i.min,i.max,i.num_verts,i.num_edges,i.seed)})
    elif options.inputs_list_file is not None:
        input_solns = DataSet.read_from_file(InputSolution, options.inputs_list_file)

    # prepare for a correctness data collection
    if options.correctness:
        num_on += 1
        get_results_for_rev = lambda rev : DataSet.read_from_file(CorrResult, CorrResult.get_path_to(rev))
        options.inputs_list_file_arg = '' if options.inputs_list_file is None else ' -l ' + options.inputs_list_file
        collect_missing_data = lambda x,y,z: collect_missing_correctness_data(x,y,z,options.inputs_list_file_arg)

    # make sure no more than 1 type of data collection was specified
    if num_on > 1:
        parser.error('at most one of -c, -d, and -e may be specified')
    elif num_on == 0:
        # prepare for a performance data collection (default if nothing else is specified)
        get_results_for_rev = lambda rev : DataSet.read_from_file(PerfResult, PerfResult.get_path_to(rev))
        collect_missing_data = collect_missing_performance_data

    # prepare the inputs and revisions for non-weight data collection schemes
    if options.num_vertices == 0:
        # get all performance inputs if we are not collecting for a single graph
        if input_solns is None:
            input_path = InputSolution.get_path_to(1, 0, 0, 100000)
            input_solns = DataSet.read_from_file(InputSolution, input_path)

        # prepare the revisions to collect data for
        if options.rev is not None:
            revs = [options.rev]
        else:
            revs = get_tracked_revs()

    # pull out just the Input object (results are keyed on these, not InputSolution)
    inputs = [i.input() for i in input_solns.dataset.values()]

    # collect the data!
    what_to_do = None if options.list_only else collect_missing_data
    if collect_data(revs, get_results_for_rev, inputs, what_to_do, options.num_runs):
        print 'All requested data has been collected!'

def collect_data(revs, get_results_for_rev, inputs, collect_missing_data, num_runs):
    root_len = len(get_path_to_project_root())
    missing_none = True
    for rev in revs:
        # load info about the results we have to far for this rev
        try:
            results = get_results_for_rev(rev)  # results is an [DataSet]
        except DataError, e:
            missing_none = False
            if rev is None:
                print >> sys.stderr, 'skipped data collection: %s' % e
            else:
                print >> sys.stderr, '%s skipped: %s' % (rev, e)
            continue

        # for each input, make sure we have run it on this rev
        for i in inputs: # inputs is an [Input]
            n = get_num_runs_missing_for_data(results, i, num_runs)
            if n > 0:
                msg = None
                if collect_missing_data is None:
                    missing_none = False
                    msg = 'missing'
                elif not collect_missing_data(i, rev, num_runs-n, n):
                    missing_none = False
                    msg = 'failed to collect'
                if msg is not None:
                    if rev is None:
                        print '%s: %s runsLeft=%u' % (msg, str(i)[root_len:], n)
                    else:
                        print '%s: %s rev=%s runsLeft=%u' % (msg, str(i)[root_len:], rev, n)

    return missing_none

if __name__ == "__main__":
    sys.exit(main())
