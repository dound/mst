#!/usr/bin/env python

from mstutil import die, get_path_to_checker_binary, get_path_to_mst_binary, quiet_remove, random_tmp_filename
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

    # compare them
    os.system('diff %s %s && echo No difference!' % (checker_out, mst_out))
    quiet_remove(mst_out)
    quiet_remove(checker_out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
