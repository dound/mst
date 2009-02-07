#!/usr/bin/env python

from mstutil import get_path_to_mst_binary, random_tmp_filename
from optparse import OptionParser
import os, sys

def benchmark(mst_binary, input_graph, out, do_log):
    print "measuring performance of '%s' on '%s' saving to '%s' (log=%s)" % (mst_binary, input_graph, out, str(do_log))

def determine_weight(mst_binary, input_graph, out, do_log):
    print "using '%s' to determine MST weight of '%s' saving to '%s' (log=%s)" % (mst_binary, input_graph, out, str(do_log))

def test_mst(test_type, mst_binary, input_graph, out, do_log):
    if test_type == "perf":
        benchmark(mst_binary, input_graph, out, do_log)
    else:
        determine_weight(mst_binary, input_graph, out, do_log)

__input_graph_to_cleanup = None
__files_to_cleanup = []
def __cleanup_and_exit(code=0):
    for fn in __files_to_cleanup:
        os.system('rm -f ' + fn)
    if __input_graph_to_cleanup is not None:
        os.system('rm -f ' + __input_graph_to_cleanup)
    sys.exit(code)

def __generate_input_graph(argstr):
    """Generate a graph from the specified string of arguments and return the file it is saved in."""
    global __input_graph_to_cleanup
    input_graph = random_tmp_filename(10)
    __input_graph_to_cleanup = input_graph
    cmd = './generate_input.py %s > %s' % (argstr, input_graph)
    ret = os.system(cmd)
    if ret != 0:
        print 'error: aborting test (input generation failed): ./generate_input.py %s' % argstr
        __cleanup_and_exit(ret)
    return input_graph

def main():
    usage = """usage: %prog [options]
Tests the performance of the MST implementation or uses it to find the weight of an MST.

GEN_ARGS can be arbitrary arguments or one of the following special arguments to generate a complete graph:
  edge: random uniform edge weights [0, 1]
  locN: randomly position vertices in N-dimensional space with axis ranges [0,1]

TYPE can be one of the following:
  perf - performance benchmark (CPU time)
  weight - MST weight computation"""
    parser = OptionParser(usage)
    parser.add_option("-c", "--check",
                      metavar="CORRECT_OUTPUT_FILE",
                      help="check output using check_output.py (only for the first run; exits if the check fails)")
    parser.add_option("-g", "--generate-input",
                      metavar="GEN_ARGS",
                      help="generate (and use as input) a graph from ./generate_input.py GEN_ARGS (one for each run)")
    parser.add_option("-i", "--input-file",
                      metavar="FILE",
                      help="FILE which describes the graph to use as input")
    parser.add_option("-n", "--num-runs",
                      metavar="N", type="int", default=1,
                      help="number of runs to execute")
    parser.add_option("-o", "--output-file",
                      metavar="FILE",
                      help="where to save the output MST (stdout prints to stdout) [default: do not save output]")
    parser.add_option("-r", "--rev",
                      help="SHA1 of the git revision to build the mst binary from [default: use existing binary and do not log]")
    parser.add_option("-t", "--type",
                      default="perf",
                      help="what kind of test to do [default: %default]")
    parser.add_option("-x", "--dont-log",
                      action="store_true", default=False,
                      help="do not log the result")

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.error("too many arguments: none expected")

    # validate the test type
    if options.type == "p":
        options.type = "perf"
    elif options.type == "w":
        options.type = "weight"
    elif options.type != "perf" and options.type != "weight":
        parser.error("-t must be either 'perf' or 'weight'")

    # get the input file
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

        input_graph = __generate_input_graph(gen_input_args)
    else:
        parser.error("at least one of -g and -i must be used to specify the input graph")

    if options.num_runs < 1:
        parser.error("-n must be at least 1")

    # get the mst binary we want to test with
    mst_binary = random_tmp_filename(10)
    __files_to_cleanup.append(mst_binary)
    if options.rev is None:
        options.dont_log = True  # no logging allowed on binaries which aren't checked in to the repo
        options.rev = ""         # tells the script to just use the current revision
    cmd = './copy_and_build_from_rev.sh %s %s %s' % (get_path_to_mst_binary(), mst_binary, options.rev)
    ret = os.system(cmd)
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
    test_mst(options.type, mst_binary, input_graph, out, not options.dont_log)
    if options.check is not None:
        correct_out = options.check
        if options.dont_log:
            log_opt = "-x"
        else:
            log_opt = ""
        cmd = "./check_output.py -i %s %s %s %s" % (input_graph, log_opt, correct_out, out)
        ret = os.system(cmd)
    else:
        ret = 0

    # exit if checking failed
    if ret != 0:
        print "error: check failed (bailing out)"
        __cleanup_and_exit(ret)

    # remaining runs, if any
    for _ in range(options.num_runs-1):
        if gen_input_args is not None:
            os.system('rm -f ' + __input_graph_to_cleanup)
            input_graph = __generate_input_graph(gen_input_args)
        test_mst(options.type, mst_binary, input_graph, "/dev/null", not options.dont_log)

    __cleanup_and_exit()

if __name__ == "__main__":
    sys.exit(main())
