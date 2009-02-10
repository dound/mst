#!/usr/bin/env python

from generate_input import main as generate_input
from mstutil import get_path_to_mst_binary, get_path_to_tools_root, quiet_remove, random_tmp_filename
from optparse import OptionParser
import os, sys

# include-with-submit # note: this file has been automatically altered for submission to reduce dependencies
# include-with-submit #       on functionality not strictly needed for the 'random' binary to work
# include-with-submit get_path_to_tools_root = lambda : './'

def benchmark(mst_binary, input_graph, out, do_log):
    print "measuring performance of '%s' on '%s' saving to '%s' (log=%s)" % (mst_binary, input_graph, out, str(do_log))

def determine_weight(mst_binary, input_graph, out, do_log):
    print "using '%s' to determine MST weight of '%s' saving to '%s' (log=%s)" % (mst_binary, input_graph, out, str(do_log))

def test_mst(is_test_perf, mst_binary, input_graph, out, do_log):
    if is_test_perf:
        benchmark(mst_binary, input_graph, out, do_log)
    else:
        determine_weight(mst_binary, input_graph, out, do_log)

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
    elif options.check:
        out = random_tmp_filename(10)
        __files_to_cleanup.append(out)
    else:
        out = "/dev/null"

    # do the first run (and check the output if requested)
    test_mst(is_test_perf, mst_binary, input_graph, out, not options.dont_log)
    if options.check:
        if options.dont_log_any:
            log_opt = "-x"
        else:
            log_opt = ""
        cmd = "check_output.py -i %s %s %s" % (input_graph, log_opt, out)
        ret = os.system(get_path_to_tools_root() + cmd)
    else:
        ret = 0

    # exit if checking failed
    if ret != 0:
        print "error: check failed (bailing out)"
        __cleanup_and_exit(ret)

    # remaining runs, if any
    for _ in range(options.num_runs-1):
        if options.trial_num >= 0:
            options.trial_num += 1
        if gen_input_args is not None:
            quiet_remove(__input_graph_to_cleanup)
            input_graph = __generate_input_graph(gen_input_args)
        test_mst(is_test_perf, mst_binary, input_graph, "/dev/null", not options.dont_log)

    __cleanup_and_exit()

if __name__ == "__main__":
    sys.exit(main())
