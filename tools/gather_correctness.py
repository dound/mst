#!/usr/bin/env python

from data import DataSet, InputSolution
from check_output import get_and_log_mst_weight_from_checker
from generate_input import main as generate_input
import sys, time

if len(sys.argv) != 2:
    print 'usage: gather_correctness.py LOG_FN'
    sys.exit(-1)

# get the file to read inputs from
logfn = sys.argv[1]
ds = DataSet.read_from_file(InputSolution, logfn)

# compute correctness for each input
inputs = ds.dataset.keys() # Input objects
inputs.sort()
on = 0
for i in inputs:
    on += 1
    # figure out how to generate the graph and where it will be sotred
    argstr = '-mt ' + i.make_args_for_generate_input()
    input_graph = generate_input(argstr.split(), get_output_name_only=True)
    print time.ctime(time.time()) + ' input # ' + str(on) + ' => gathering correctness data for ' + argstr

    # generate the graph
    generate_input(argstr.split())

    # compute the weight for the graph
    get_and_log_mst_weight_from_checker(input_graph, force_recompute=False, inputslogfn=logfn)
