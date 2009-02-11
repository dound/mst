#!/usr/bin/env python

from check_output import check, CheckerError, extract_answer
from data import DataError, DataSet, PerfResult, WeightResult, CORRECT, INCORRECT
from data import extract_input_footer, ExtractInputFooterError
from generate_input import main as generate_input
from mstutil import get_path_to_mst_binary, get_path_to_tools_root, quiet_remove, random_tmp_filename
from optparse import OptionParser
import os, sys

# include-with-submit # note: this file has been automatically altered for submission to reduce dependencies
# include-with-submit #       on functionality not strictly needed for the 'random' binary to work
# include-with-submit get_path_to_tools_root = lambda : './'

def benchmark(mst_binary, input_graph, out, rev, trial_num, for_time):
    print "benchmarking '%s' (rev=%s, trial=%u, out=%s)" % (input_graph, rev, trial_num, out)

    # run mst (and time it)
    time_file = random_tmp_filename(10)
    cmd = '/usr/bin/time -f %%U -o %s %s %s > %s' % (time_file, mst_binary, input_graph, out)
    ret = os.system(cmd)
    if ret != 0:
        print >> sys.stderr, "failed to run mst: " + cmd
        return
    try:
        time_sec = extract_answer(time_file)
    except CheckerError, e:
        print >> sys.stderr, "failed to read time file: " + e
        return
    quiet_remove(time_file)

    # try to get the weight (if we output the result somewhere)
    if out != "/dev/null":
        try:
            mst_weight = extract_answer(out)
        except CheckerError, e:
            print >> sys.stderr, "failed to read weight file: " + e
            return
        str_mst_weight = '  mst_weight=' + str(mst_weight)
    else:
        str_mst_weight = ''

    # check to see if we are supposed to log the result
    if trial_num < 0:
        print ('%s ===> time=%.2f'+str_mst_weight) % (cmd, time_sec)
        return

    # extract properties of the graph
    try:
        ti = extract_input_footer(input_graph)
    except ExtractInputFooterError, e:
        raise CheckerError("run test error: unable to extract the input footer for %s: %s" % (input_graph, e))

    # log the result
    if for_time:
        data = PerfResult(ti.num_verts, ti.num_edges, ti.seed, rev, trial_num, time_sec)
        try:
            DataSet.add_data_to_log_file(data)
        except DataError, e:
            print >> sys.stderr, "Unable to log result to file %s (was trying to log %s): %s" % (str(data), e)
    else:
        data = WeightResult(ti.dims, ti.num_verts, ti.seed, rev, trial_num, mst_weight)
        try:
            DataSet.add_data_to_log_file(data)
        except DataError, e:
            print >> sys.stderr, "Unable to log result to file %s (was trying to log %s): %s" % (str(data), e)

def test_mst(is_test_perf, mst_binary, input_graph, out, do_log, rev, trial_num):
    trial_num = -1 if not do_log else trial_num
    benchmark(mst_binary, input_graph, out, rev, trial_num, is_test_perf)

__input_graph_to_cleanup = None
__files_to_cleanup = []
def __cleanup_and_exit(code=0):
    for fn in __files_to_cleanup:
        quiet_remove(fn)
    if __input_graph_to_cleanup is not None:
        quiet_remove(__input_graph_to_cleanup)
    sys.exit(code)

def __generate_input_graph(argstr):
    """Generate a graph from the specified string of arguments and return the file it is saved in."""
    global __input_graph_to_cleanup
    input_graph = random_tmp_filename(10)
    __input_graph_to_cleanup = input_graph
    args = (argstr + ' -mqto ' + input_graph).split()

    try:
        errstr = "unknown error"
        ret = generate_input(args)
    except Exception, errstr:
        ret = -1
    if ret != 0:
        print 'error: aborting test (input generation failed): %s: %s' % (errstr, argstr)
        __cleanup_and_exit(ret)
    return input_graph

def main():
    usage = """usage: %prog [options]
Tests the performance of the MST implementation.  Alternatively, when -g is used
with a special argument (below), this determines the weight of the MST.

GEN_ARGS can be arbitrary arguments (to test performance) or one of the
following special arguments to generate a complete graph (for MST weight
computation only):
  edge,NUM_VERTICES: random uniform edge weights [0, 1]
  locN,NUM_VERTICES: randomly position vertices in N-dimensional space with axis ranges [0,1]"""
    parser = OptionParser(usage)
    parser.add_option("-c", "--check",
                      action="store_true", default=False,
                      help="whether to check output using check_output.py (only for the first run; exits if the check fails)")
    parser.add_option("-g", "--generate-input",
                      metavar="GEN_ARGS",
                      help="generate (and use as input) a graph from generate_input.py GEN_ARGS (one for each run); -mqt will also be passed")
    parser.add_option("-i", "--input-file",
                      metavar="FILE",
                      help="FILE which describes the graph to use as input")
    parser.add_option("-n", "--num-runs",
                      metavar="N", type="int", default=1,
                      help="number of runs to execute [default: %default]")
    parser.add_option("-o", "--output-file",
                      metavar="FILE",
                      help="where to save the output MST (stdout prints to stdout) [default: do not save output]")
    parser.add_option("-q", "--quiet",
                      action="store_true", default=False,
                      help="do not print extraneous info to stdout")
    parser.add_option("-r", "--rev",
                      help="SHA1 of the git revision to build the mst binary from [default: use existing binary and do not log]")
    parser.add_option("-x", "--dont-log",
                      action="store_true", default=False,
                      help="do not log the result")
    parser.add_option("-t", "--trial-num",
                      type="int", default=-1,
                      help="run/trial identifier [default: do not log the trial, so ignore it]")

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.error("too many arguments: none expected")

    # get the input file
    is_test_perf = True
    gen_input_args = None
    if options.generate_input is not None and options.input_file is not None:
        parser.error("-g and -i are mutually exclusive")
    elif options.input_file is not None:
        input_graph = options.input_file
    elif options.generate_input is not None:
        s = options.generate_input.split(',',2)
        gen_type = s[0]
        if gen_type == "edge":
            if len(s) != 2:
                parser.error('-g edge,NUM_VERTICES form requires exactly these args')
            gen_input_args = "-p 15 -e 0.0,1.0 %s" % s[1]
        elif len(gen_type)==4 and gen_type[:3] == "loc":
            if len(s) != 2:
                parser.error('-g %s,NUM_VERTICES form requires exactly these args' % gen_type)
            d = gen_type[3:]
            gen_input_args = "-p 15 -v %s,0.0,1.0 %s" % (d, s[1])

        # if it was not a special case, just pass the args straight through
        if gen_input_args is None:
            gen_input_args = options.generate_input
        else:
            is_test_perf = False

        input_graph = __generate_input_graph(gen_input_args)
    else:
        parser.error("at least one of -g and -i must be used to specify the input graph")

    if options.num_runs < 1:
        parser.error("-n must be at least 1")

    if options.trial_num < 0:
        options.dont_log = True

    # get the mst binary we want to test with
    mst_binary = random_tmp_filename(10)
    __files_to_cleanup.append(mst_binary)
    if options.rev is None:
        options.dont_log = True  # no logging allowed on binaries which aren't checked in to the repo
        options.trial_num = -1
        options.rev = ""         # tells the script to just use the current revision
    cmd = 'copy_and_build_from_rev.sh %s %s %s' % (get_path_to_mst_binary(), mst_binary, options.rev)
    if options.quiet:
        cmd += ' > /dev/null'
    ret = os.system(get_path_to_tools_root() + cmd) # exclude-from-submit
    # include-with-submit ret = 0
    # include-with-submit mst_binary = './mst'
    if ret != 0:
        print 'error: unable to copy and build the mst binary'
        __cleanup_and_exit(ret)

    # prepare the output file
    if options.output_file:
        out = options.output_file
        out_is_temporary = False
    else:
        if options.check:
            out = random_tmp_filename(10)
            __files_to_cleanup.append(out)
            out_is_temporary = True
        else:
            out = "/dev/null"

    # do the first run (and check the output if requested)
    test_mst(is_test_perf, mst_binary, input_graph, out, not options.dont_log, options.rev, options.trial_num)
    if options.check:
        rev = None if options.rev is "" else options.rev
        run = None if options.trial_num < 0 else options.trial_num
        try:
            ret = check(input_graph, out, 1, False, rev, run)
            errmsg = ''
        except CheckerError, e:
            ret = INCORRECT
            errmsg = ': ' + str(e)

        if out_is_temporary:
            quiet_remove(out)
        if ret != CORRECT:
            print '%s ===> INCORRECT *** CORRECTNESS FAILED'
            __cleanup_and_exit(-1)
        else:
            print '%s ===> CORRECT'

    # remaining runs, if any
    for _ in range(options.num_runs-1):
        if options.trial_num >= 0:
            options.trial_num += 1
        if gen_input_args is not None:
            quiet_remove(__input_graph_to_cleanup)
            input_graph = __generate_input_graph(gen_input_args)
        test_mst(is_test_perf, mst_binary, input_graph, "/dev/null", not options.dont_log, options.rev, options.trial_num)

    __cleanup_and_exit()

if __name__ == "__main__":
    sys.exit(main())
