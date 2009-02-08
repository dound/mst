#!/usr/bin/env python

from mstutil import die, get_path_to_inputs, get_path_to_checker_binary
from optparse import OptionParser
import os, sys

def get_answer(fn, what):
    # get the correct answer
    try:
        fh = open(fn)
        try:
            ans = float(fh.readline())
        except ValueError:
            die("check_output.py: error: invalid answer in %s file %s" % (what, fn))
        fh.close()
    except IOError, errstr:
        die("check_output.py: error: failed to read %s data from %s" % (what, fn))
    return ans

def check(input_graph, output_to_test, tolerance, verbose, do_log):
    print "check '%s' with solution '%s' based on input '%s' (verbose=%s, log=%s)" % \
        (output_to_test, output_correct, input_graph, str(verbose), str(do_log))

    corr_file = get_path_to_inputs() + 'corr/%s' % os.basename(input_graph)

    # make the correctness file which caches the right answer if it does not exist
    if not os.path.exists(corr_file):
        checker = get_path_to_checker_binary(True)
        if os.system('%s %s > %s' % (checker, input_graph, corr_file)) != 0:
            die("check_output.py: error: failed to generate new correctness data for " + input_graph)

    # get the output answers
    ans_corr = get_answer(corr_file, 'correctness')
    ans_out = get_answer(output_to_test, 'output file being tested')

    # are the same?
    fmt = '%.' + tolerance + 'f'
    str_ans_corr = fmt % ans_corr
    str_ans_out = fmt % ans_out
    if str_ans_corr == str_ans_out:
        code = 0    # succcess!
    else:
        print >> stderr, "correctness FAILED: %s (correct is %s, output had %s)" % (input_graph, str_ans_corr, str_ans_out)
        code = -1

    # log the result of the correctness check
    # TODO ...

def main():
    usage = """usage: %prog [options] OUTPUT_TO_CHECK
Checks the validity of an MST.  Exits with code 0 on success.  Otherwise, it
prints an error message and exits with a non-zero code."""
    parser = OptionParser(usage)
    parser.add_option("-i", "--input_graph",
                      metavar="FILE",
                      help="the input graph which corresponds to these outputs")
    parser.add_option("-q", "--quick",
                      action="store_true", default=False,
                      help="only check the output MST weight (implied if INPUT is omitted)")
    parser.add_option("-t", "--tolerance",
                      type="int", default=1,
                      help="number of decimal places of the weight check which must match exactly [default: %default]")
    parser.add_option("-v", "--verbose",
                      action="store_true", default=False,
                      help="if the output is incorrect this will print a detailed explanation")
    parser.add_option("-x", "--dont-log",
                      action="store_true", default=False,
                      help="do not log the result")

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("missing argument: OUTPUT_TO_CHECK is required")
    elif len(args) > 1:
        parser.error("too many arguments")

    output_to_test = args[0]

    if not options.quick:
        input_graph = options.input_graph
    else:
        input_graph = None

    check(input_graph, output_to_test, options.tolerance, options.verbose, not options.dont_log)

if __name__ == "__main__":
    sys.exit(main())
