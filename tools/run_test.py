#!/usr/bin/env python

from check_output import check, CheckerError, extract_answer
from data import DataError, DataSet, PerfResult, WeightResult, CORRECT, INCORRECT
from data import extract_input_footer, ExtractInputFooterError, ppinput
from generate_input import main as generate_input, is_input_for_part2
from mstutil import get_path_to_mst_binary, get_path_to_tools_root, quiet_remove, random_tmp_filename
from optparse import OptionParser
from socket import gethostname
import os, sys

# include-with-submit # note: this file has been automatically altered for submission to reduce dependencies
# include-with-submit #       on functionality not strictly needed for the 'random' binary to work
# include-with-submit get_path_to_tools_root = lambda : './'

def print_benchmark(input_graph, out, rev, trial_num, for_time):
    """Returns whether time may be logged."""
    msg = "benchmarking %s (rev=" % input_graph
    msg += 'current' if rev == '' else rev
    msg += ', '
    ret = True
    if not for_time:
        msg += 'logging weight'
    elif trial_num is None or trial_num < 0:
        msg += 'not logging result'
    else:
        if gethostname()[:4] == 'myth':
            msg += 'logging time for trial %u' % trial_num
        else:
            msg += 'cannot log performance on %s (myth only test)' % gethostname()
            ret = False
    print msg + ', out=%s)' % out
    return ret

def benchmark(mst_binary, input_graph, out, rev, trial_num, for_time):
    rel_input_graph = ppinput(input_graph)
    if not print_benchmark(rel_input_graph, out, rev, trial_num, for_time):
        trial_num = -1  # cancel logging

    # determine how to save the output
    kill_out = False
    if for_time or out != '/dev/null':
        # disable /dev/null for performance experiments so we can get the weight for now ...
        if out == '/dev/null':
            out = random_tmp_filename(10, 'weight-for-time')
            kill_out = True

        save_cmd = '> ' + out
    else:
        # save just the first line of output so we can get the weight
        out = random_tmp_filename(10, 'weight')
        save_cmd = '| head -n 1 > ' + out
        kill_out = True

    # run mst (and time it)
    time_file = random_tmp_filename(10, 'time')
    cmd = '/usr/bin/time -f %%U -o %s %s %s %s' % (time_file, mst_binary, input_graph, save_cmd)
    ret = os.system(cmd)
    if ret != 0:
        print >> sys.stderr, "mst exited with error: " + cmd
        quiet_remove(time_file)
        return
    try:
        time_sec = extract_answer(time_file)
    except CheckerError, e:
        print >> sys.stderr, "failed to read time file: " + str(e)
        return
    quiet_remove(time_file)

    # try to get the weight (if we output the result somewhere)
    mst_weight = -1.0
    if out != "/dev/null":
        try:
            mst_weight = extract_answer(out)
        except CheckerError, e:
            print >> sys.stderr, "failed to read weight file: " + str(e)
            return
        str_mst_weight = '  mst_weight=' + str(mst_weight)
        if kill_out:
            quiet_remove(out) # was a temporary file we created
    else:
        str_mst_weight = ''

    # check to see if we are supposed to log the result
    print ('benchmark result ===> time=%.2f'+str_mst_weight) % time_sec
    if trial_num < 0 and for_time:
        return

    # extract properties of the graph
    try:
        ti = extract_input_footer(input_graph)
    except ExtractInputFooterError, e:
        raise CheckerError("run test error: unable to extract the input footer for %s: %s" % (rel_input_graph, str(e)))

    # log the result
    if for_time:
        data = PerfResult(ti.num_verts, ti.num_edges, ti.seed, rev, trial_num, time_sec, mst_weight)
        try:
            DataSet.add_data_to_log_file(data)
        except DataError, e:
            print >> sys.stderr, "Unable to log result to file %s (was trying to log %s): %s" % (data.get_path(), str(data), str(e))
    else:
        data = WeightResult(ti.dims, ti.num_verts, ti.seed, rev, trial_num, mst_weight)
        try:
            DataSet.add_data_to_log_file(data)
        except DataError, e:
            print >> sys.stderr, "Unable to log result to file %s (was trying to log %s): %s" % (data.get_path(), str(data), str(e))

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

def __generate_input_graph(argstr, cleanup_generated_input):
    """Generate a graph from the specified string of arguments and return the file it is saved in."""
    global __input_graph_to_cleanup

    try:
        if cleanup_generated_input:
            input_graph = random_tmp_filename(10, 'input')
            args = (argstr + ' -mqto ' + input_graph).split()
            __input_graph_to_cleanup = input_graph
        else:
            args = (argstr + ' -mqt').split()
            input_graph = generate_input(args, get_output_name_only=True)
            __input_graph_to_cleanup = None

        errstr = "unknown error"
        ret = generate_input(args)
    except Exception, errstr:
        ret = -1
    if ret != 0:
        print 'error: aborting test (input generation failed): %s: %s' % (str(errstr), argstr)
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
    parser.add_option("-C", "--check-exit-0",
                      action="store_true", default=False,
                      help="same as -c, but exit with code 0 even if the correctness check fails")
    parser.add_option("-g", "--generate-input",
                      metavar="GEN_ARGS",
                      help="generate (and use as input) a graph from generate_input.py GEN_ARGS (one for each run); -mqt will also be passed")
    parser.add_option("-G", "--generate-temp-input",
                      metavar="GEN_ARGS",
                      help="same as -g, but delete the graph after this script is done")
    parser.add_option("-i", "--input-file",
                      metavar="FILE",
                      help="FILE which describes the graph to use as input")
    parser.add_option("-l", "--inputs-list-file",
                      metavar="FILE",
                      help="specifies where to log correctness info (which inputs list log file) [default: inferred]")
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

    # reconcile -g and -G
    cleanup_generated_input = False
    if options.generate_temp_input is not None:
        if options.generate_input is not None:
            parser.error('only one of -g or -G may be supplied')
        else:
            options.generate_input = options.generate_temp_input
            cleanup_generated_input = True

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
            is_test_perf = not is_input_for_part2(gen_input_args.split())
        else:
            is_test_perf = False

        input_graph = __generate_input_graph(gen_input_args, cleanup_generated_input)
    else:
        parser.error("at least one of -g and -i must be used to specify the input graph")

    if options.num_runs < 1:
        parser.error("-n must be at least 1")

    if options.trial_num < 0:
        options.dont_log = True

    # get the mst binary we want to test with
    mst_binary = random_tmp_filename(10, 'mst')
    __files_to_cleanup.append(mst_binary)
    if options.rev is None or options.rev.lower() == 'current':
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

    # handle check-exit-0
    check_fail_exit_code = -1
    if options.check_exit_0:
        options.check = True
        check_fail_exit_code = 0

    # prepare the output file
    if options.output_file:
        out = options.output_file
        out_is_temporary = False
    else:
        if options.check:
            out = random_tmp_filename(10, 'out-for-checker')
            __files_to_cleanup.append(out)
            out_is_temporary = True
        else:
            if options.inputs_list_file:
                print >> sys.stderr, 'warning: -l does nothing unless -c is also specified'
            out = "/dev/null"

    # do the first run (and check the output if requested)
    test_mst(is_test_perf, mst_binary, input_graph, out, not options.dont_log, options.rev, options.trial_num)
    if options.check:
        rev = None if options.rev is "" else options.rev
        run = None if options.trial_num < 0 else options.trial_num
        try:
            ret = check(input_graph, out, 1, False, rev, run, options.inputs_list_file)
        except CheckerError, e:
            ret = INCORRECT
            print >> sys.stderr, str(e)

        if out_is_temporary:
            quiet_remove(out)

        if ret != CORRECT:
            __cleanup_and_exit(check_fail_exit_code)  # incorrectness already reported by check()
        else:
            print 'Correct - output checks out!'

    # remaining runs, if any
    for _ in range(options.num_runs-1):
        print '' # empty line
        if options.trial_num >= 0:
            options.trial_num += 1
        if gen_input_args is not None:
            if __input_graph_to_cleanup is not None:
                quiet_remove(__input_graph_to_cleanup)
            input_graph = __generate_input_graph(gen_input_args, cleanup_generated_input)
        test_mst(is_test_perf, mst_binary, input_graph, "/dev/null", not options.dont_log, options.rev, options.trial_num)

    __cleanup_and_exit()

if __name__ == "__main__":
    sys.exit(main())
