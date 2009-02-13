#!/usr/bin/env python

from check_output import extract_answer
from mstutil import get_path_to_checker_binary, get_path_to_mst_binary, get_path_to_project_root
from mstutil import die, quiet_remove, random_tmp_filename
import os, sys

def main(argv=sys.argv):
    if len(argv) != 2:
        die("""usage: check_with_diff.py INPUT_GRAPH
Checks the current mst for a given input file and reports the diff, if any.  It
does not do anything smart in terms of caching the correctness checker's output,
so it will be recomputed every time this is run.
""")
    else:
        input_graph = argv[1]

    if not os.path.exists(input_graph):
        die("%s not found" % input_graph)

    # get our mst output
    mst = get_path_to_mst_binary(make_sure_it_exists=True)
    mst_out = random_tmp_filename(10)
    if os.system('%s %s > %s' % (mst, input_graph, mst_out)) != 0:
        quiet_remove(mst_out)
        die("failed to run mst (or exited with an error code)")

    # get the checker's output
    checker = get_path_to_checker_binary(make_sure_it_exists=True)
    checker_out = random_tmp_filename(10)
    if os.system('%s %s true > %s' % (checker, input_graph, checker_out)) != 0:
        quiet_remove(mst_out)
        quiet_remove(checker_out)
        die("failed to run checker (or exited with an error code)")

    # check just the MST weight first
    mst_w = extract_answer(mst_out)
    checker_w = extract_answer(checker_out)
    fmt = '%.1f' # tolerance to 1 decimal place
    str_mst_w = fmt % mst_w
    str_checker_w = fmt % checker_w
    if str_mst_w == str_checker_w:
        print 'Weights match!'
        quiet_remove(mst_out)
        quiet_remove(checker_out)
        return 0
    else:
        print 'Weight mistmatch, comparing vertices!! (checker_mst - our_mst = %s)' % str(checker_w - mst_w)

    # sort them
    mst_out2 = random_tmp_filename(10)
    checker_out2 = random_tmp_filename(10)
    sort_and_order = get_path_to_project_root() + 'src/input/sort_and_order.py '
    os.system(sort_and_order + mst_out + ' 1 > ' + mst_out2)
    os.system(sort_and_order + checker_out + ' 1 > ' + checker_out2)

    # compare them
    os.system('diff %s %s && echo Edges are the same!' % (checker_out2, mst_out2))
    quiet_remove(mst_out)
    quiet_remove(mst_out2)
    quiet_remove(checker_out)
    quiet_remove(checker_out2)
    return 0

if __name__ == "__main__":
    sys.exit(main())
