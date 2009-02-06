#!/usr/bin/env python

from mstutil import get_path_to_mst_binary, is_mst_binary_accessible, random_tmp_filename
from optparse import OptionParser
import os, sys

def benchmark(mst_binary, input_graph, out, do_log):
    print "measuring performance of '%s' on '%s' saving to '%s' (log=%s)" % (mst_binary, input_graph, out, str(do_log))

def determine_weight(mst_binary, input_graph, out, do_log):
    print "measuring performance of '%s' on '%s' saving to '%s' (log=%s)" % (mst_binary, input_graph, out, str(do_log))

def test_mst(type, mst_binary, input_graph, out, do_log):
    if type == "perf":
        benchmark(mst_binary, input_graph, out, do_log)
    else:
        determine_time(mst_binary, input_graph, out, do_log)

__files_to_cleanup = []
def cleanup_and_exit(code=0):
    for fn in __files_to_cleanup:
        os.system('rm -f ' + fn)
    sys.exit(code)

def main():
    desc  = "Measures the performance of an MST."
    extra = """TYPE can be one of the following:
  perf - performance benchmark (CPU time)
  weight - MST weight computation"""
        
    usage = "usage: %prog [options]\n" + desc + '\n\n' + extra
    parser = OptionParser(usage)
    parser.add_option("-r", "--rev",
                      help="SHA1 of the git revision to build the mst binary from [default: use the currently built binary and do not log]"),
    parser.add_option("-o", "--output-file",
                      metavar="FILE",
                      help="where to save the output MST (stdout prints to stdout) [default: do not save output]")
    parser.add_option("-c", "--check",
                      metavar="CORRECT_OUTPUT_FILE",
                      help="check output using check_output.py (only for the first run; exits if the check fails)")
    parser.add_option("-n", "--num-runs",
                      metavar="NUM", type="int", default=1,
                      help="number of runs to execute")
    parser.add_option("-t", "--type",
                      default="perf",
                      help="what kind of test to do [default: %default]")
    parser.add_option("-x", "--dont-log",
                      action="store_true", default=False,
                      help="do not log the result")

    (options, args) = parser.parse_args()

    # validate the test type
    if options.type == "p":
        options.type = "perf"
    elif options.type == "w":
        options.type = "weight"
    elif options.test != "perf" and options.test != "weight":
        parser.error("-t must be either 'perf' or 'weight'")
    if len(args) < 1:
        parser.error("not enough arguments: INPUT_GRAPH is required")
    elif len(args) > 1:
        parser.error("too many arguments: only expected INPUT_GRAPH")

    input_graph = args[0]
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
        cleanup_and_exit(ret)

    # prepare the output file
    if options.output_file:
        out = options.output_file
    elif options.check:
        out = random_tmp_filename(10)
        __files_to_cleanup.append(out_is_tmp)
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
        cleanup_and_exit(ret)

    # remaining runs, if any
    for _ in range(options.num_runs-1):
        test_mst(options.type, mst_binary, input_graph, "/dev/null", not options.dont_log)

    cleanup_and_exit()

if __name__ == "__main__":
    sys.exit(main())
