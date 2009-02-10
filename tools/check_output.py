#!/usr/bin/env python

from generate_input import ExtractInputFooterError, extract_input_footer
from input_tracking import get_tracked_input_fn, get_tracked_inputs, save_tracked_inputs
from mstutil import get_path_to_checker_binary, random_tmp_filename
from optparse import OptionParser
import os, sys

class CheckerError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def extract_answer(fn):
    """Get the answer from output from either mst or the checker"""
    try:
        fh = open(fn)
        try:
            ans = float(fh.readline())
            return ans
        except ValueError, e:
            raise CheckerError("checker error: invalid answer in file %s: %s" % (fn, e))
        fh.close()
    except IOError, errstr:
        raise CheckerError("checker error: failed to read data from %s: %s" % (fn, errstr))

def compute_mst_weight(input_graph):
    """Computes and returns the MST weight of input_graph using the checker"""
    corr_file = random_tmp_filename(10)
    try:
        w = __compute_mst_weight(input_graph, corr_file)
        os.remove(corr_file)
        return w
    except CheckerError:
        os.remove(corr_file)
        raise

def __compute_mst_weight(input_graph, corr_file):
    """Internal method to actual compute the MST weight of input_graph"""
    checker = get_path_to_checker_binary(True)
    ret = os.system('%s %s > %s' % (checker, input_graph, corr_file))
    if ret == 0:
        return extract_answer(corr_file)
    else:
        raise CheckerError("checker error: failed to generate output for " + input_graph)

def get_and_log_mst_weight_from_checker(input_graph, force_recompute=False):
    """Returns the weight of input_graph's MST according to the checker.  If
    force_recompute is not True, then it will check the input log cache to see
    if we already know the answer first.  Logs the result."""
    try:
        ti = extract_input_footer(input_graph)
    except ExtractInputFooterError, e:
        raise CheckerError("checker error: unable to extract the input footer for %s: %s" % (input_graph, e))

    # load in the inputs in the category of input_graph
    logfn = get_tracked_input_fn(ti.precision, ti.dimensionality, ti.min, ti.max)
    inputs = get_tracked_inputs(logfn)
    if inputs.has_key(ti):
        ti = inputs[ti]
        do_log = True
    else:
        # if we weren't tracking the input before, don't start now
        do_log = False

    # see if we already know the answer
    if not force_recompute:
        if ti.mst_weight >= 0:
            return ti.mst_weight  # cache hit!

    # compute the answer and (if specified) save it
    w = compute_mst_weight(input_graph, 'correctness')
    if do_log:
        ti.update_mst_weight(w)
        save_tracked_inputs(logfn, inputs)
    return w

def check(input_graph, output_to_test, tolerance, force_recompute, do_log):
    """Checks whether the MST weight of input_graph matches output_to_test to
    the specified tolerance.
    @param force_recompute  whether the checker's MST weight can come from cache
    @param do_log           whether to log the result of the correctness check
    """
    ans_out = extract_answer(output_to_test)
    ans_corr = get_and_log_mst_weight_from_checker(input_graph, force_recompute, do_log)

    # are they the same?
    fmt = '%.' + tolerance + 'f'
    str_ans_corr = fmt % ans_corr
    str_ans_out = fmt % ans_out
    if str_ans_corr == str_ans_out:
        code = 0    # succcess!
    else:
        print >> sys.stderr, "correctness FAILED: %s (correct is %s, output had %s)" % (input_graph, str_ans_corr, str_ans_out)
        code = -1

    # log the result of the correctness check
    if do_log:
        pass # TODO

def main(argv=sys.argv[1:]):
    usage = """usage: %prog [options] INPUT_GRAPH OUTPUT_TO_CHECK
Checks the validity of an MST.  Exits with code 0 on success.  Otherwise, it
prints an error message and exits with a non-zero code."""
    parser = OptionParser(usage)
    parser.add_option("-f", "--force-recompute",
                      action="store_true", default=False,
                      help="recomputes the MST weight with the checker even if we have a cached value")
    parser.add_option("-t", "--tolerance",
                      type="int", default=1,
                      help="number of decimal places of the weight check which must match exactly [default: %default]")
    parser.add_option("-x", "--dont-log",
                      action="store_true", default=False,
                      help="do not log the result")

    (options, args) = parser.parse_args(argv)
    if len(args) < 2:
        parser.error("missing argument: INPUT_GRAPH and OUTPUT_TO_CHECK is required")
    elif len(args) > 2:
        parser.error("too many arguments")

    input_graph = args[0]
    output_to_test = args[1]
    return check(input_graph, output_to_test, options.tolerance, options.force_recompute, not options.dont_log)

if __name__ == "__main__":
    sys.exit(main())
