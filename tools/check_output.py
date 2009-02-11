#!/usr/bin/env python

from data import DataError, DataSet, InputSolution, CorrResult, CORRECT, INCORRECT
from data import extract_input_footer, ExtractInputFooterError, ppinput
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
    corr_file = random_tmp_filename(10, 'corr')
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
        raise CheckerError("checker error: failed to generate output for " + ppinput(input_graph))

def get_and_log_mst_weight_from_checker(input_graph, force_recompute=False, inputslogfn=None):
    """Returns the a 2-tuple of (input, weight).  If force_recompute is not
    True, then it will check the input log cache to see if we already know the
    answer first.  Logs the result."""
    try:
        ti = extract_input_footer(input_graph)
    except ExtractInputFooterError, e:
        raise CheckerError("checker error: unable to extract the input footer for %s: %s" % (ppinput(input_graph), e))

    # load in the inputs in the category of input_graph
    if inputslogfn is None:
        logfn = InputSolution.get_path_to(ti.prec, ti.dims, ti.min, ti.max)
    else:
        logfn = inputslogfn
    ds = DataSet.read_from_file(InputSolution, logfn)
    if ds.dataset.has_key(ti):
        input_soln = ds.dataset[ti]
        do_log = True

        # see if we already know the answer
        if not force_recompute:
            if input_soln.has_mst_weight():
                return (ti, input_soln.mst_weight)  # cache hit!
    else:
        # if we weren't tracking the input before, don't start now
        do_log = False

    # compute the answer and (if specified) save it
    w = compute_mst_weight(input_graph)
    if do_log:
        if input_soln.update_mst_weight(w):
            ds.save_to_file(logfn)
    return (ti, w)

def check(input_graph, output_to_test, tolerance, force_recompute, rev=None, run=None, inputslogfn=None):
    """Checks whether the MST weight of input_graph matches output_to_test to
    the specified tolerance.
    @param force_recompute  whether the checker's MST weight can come from cache
    @param rev              what revision to log this result under
    @param run              what run number to log this result under
    @param inputslogfn      filename of the correctness log (if not provided, it is inferred)
    """
    ans_out = extract_answer(output_to_test)
    (ti, ans_corr) = get_and_log_mst_weight_from_checker(input_graph, force_recompute, inputslogfn)

    # are they the same?
    fmt = '%.' + str(tolerance) + 'f'
    str_ans_corr = fmt % ans_corr
    str_ans_out = fmt % ans_out
    if str_ans_corr == str_ans_out:
        outcome = CORRECT
    else:
        print >> sys.stderr, "correctness FAILED: %s (correct is %s, output had %s)" % (ppinput(input_graph), str_ans_corr, str_ans_out)
        outcome = INCORRECT

    # log the result of the correctness check
    if rev is not None and run is not None:
        data = CorrResult(ti.dims, ti.min, ti.max, ti.num_verts, ti.num_edges, ti.seed, rev, run, outcome)
        try:
            DataSet.add_data_to_log_file(data)
            print 'logged correctness result to ' + data.get_path()
        except DataError, e:
            fmt = "Unable to log result to file %s (correct is %s, output had %s): %s"
            print >> sys.stderr, fmt % (ppinput(input_graph), str_ans_corr, str_ans_out, e)

    return outcome

def main(argv=sys.argv[1:]):
    usage = """usage: %prog [options] INPUT_GRAPH OUTPUT_TO_CHECK
Checks the validity of an MST.  Exits with code 0 on success.  Otherwise, it
prints an error message and exits with a non-zero code.  Does not log the result."""
    parser = OptionParser(usage)
    parser.add_option("-f", "--force-recompute",
                      action="store_true", default=False,
                      help="recomputes the MST weight with the checker even if we have a cached value")
    parser.add_option("-t", "--tolerance",
                      type="int", default=1,
                      help="number of decimal places of the weight check which must match exactly [default: %default]")

    (options, args) = parser.parse_args(argv)
    if len(args) < 2:
        parser.error("missing argument: INPUT_GRAPH and OUTPUT_TO_CHECK is required")
    elif len(args) > 2:
        parser.error("too many arguments")

    input_graph = args[0]
    output_to_test = args[1]
    outcome = check(input_graph, output_to_test, options.tolerance, options.force_recompute)
    return (0 if outcome==CORRECT else -1)

if __name__ == "__main__":
    sys.exit(main())
