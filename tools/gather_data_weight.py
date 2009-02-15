#!/usr/bin/env python

from data import DataSet, WeightResult
from result import ResultAccumulator
from mstutil import get_path_to_project_root
import os, sys

DATA_PATH = get_path_to_project_root() + 'writeup/data/weight/'

def gather_weight_data(wtype):
    # get the results
    results = {} # maps |V| to ResultAccumulator
    ds = DataSet.read_from_file(WeightResult, WeightResult.get_path_to(wtype))
    for data in ds.dataset.values():
        result = results.get(data.input().num_verts)
        if result is None:
            result = ResultAccumulator(data.mst_weight)
            results[data.input().num_verts] = result
        else:
            result.add_data(data.mst_weight)

    try:
        # open a file to output to
        fh = open(DATA_PATH + wtype + '.dat', 'w')

        # compute relevant stats and output them
        print >> fh, '#|V|\tLower\tAverage\tUpper  (Lower/Upper from 99% CI)'
        keys = results.keys()
        keys.sort()
        for num_verts in keys:
            r = results[num_verts]
            r.compute_stats()
            print >> fh, '%u\t%.3f\t%.3f\t%.3f' % (num_verts, r.lower99, r.mean, r.upper99)
        fh.close()
        return 0
    except IOError, e:
        print sys.stderr, "failed to write file: " + str(e)
        return -1

def main():
    try:
        os.makedirs(DATA_PATH)
    except OSError:
        pass
    gather_weight_data('edge')
    gather_weight_data('loc2')
    gather_weight_data('loc3')
    gather_weight_data('loc4')

if __name__ == "__main__":
    sys.exit(main())
