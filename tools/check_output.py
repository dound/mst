#!/usr/bin/env python

from optparse import OptionParser
import sys

def check(input_graph, output_to_test, output_correct, verbose, do_log):
    print "check '%s' with solution '%s' based on input '%s' (verbose=%s, log=%s)" % \
        (output_to_test, output_correct, input_graph, str(verbose), str(do_log))

def main():
    desc  = "Checks the validity of an MST.  Exits with code 0 on success."
    usage = "usage: %prog [options] CORRECT_OUTPUT OUTPUT_TO_CHECK\n" + desc
    parser = OptionParser(usage)
    parser.add_option("-i", "--input_graph",
                      metavar="FILE",
                      help="the input graph which corresponds to these outputs")
    parser.add_option("-q", "--quick",
                      action="store_true", default=False,
                      help="only check the output MST weight (implied if INPUT is omitted)")
    parser.add_option("-v", "--verbose",
                      action="store_true", default=False,
                      help="if the output is incorrect this will print a detailed explanation")
    parser.add_option("-x", "--dont-log",
                      action="store_true", default=False,
                      help="do not log the result")

    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.error("not enough arguments: CORRECT_OUTPUT and OUTPUT_TO_CHECK are both required")
    elif len(args) > 2:
        parser.error("too many arguments")

    output_correct = args[0]
    output_to_test = args[1]
    
    if not options.quick:
        input_graph = options.input_graph
    else:
        input_graph = None

    check(input_graph, output_to_test, output_correct, options.verbose, not options.dont_log)

if __name__ == "__main__":
    sys.exit(main())
