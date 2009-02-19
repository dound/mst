#!/usr/bin/env python

from data import DataSet, PerfResult, get_tracked_algs_and_revs
from generate_input import get_density, get_percent_of_max
from result import ResultAccumulator
from mstutil import get_path_to_project_root, quiet_remove
import os, sys

DATA_PATH = get_path_to_project_root() + 'writeup/data/perf/'

# figure out which revisions correspond to which algorithms
TRACKED = get_tracked_algs_and_revs()

# vertex values to create data files for
IMPORTANT_VERTS = [250, 700, 4473, all]

# confidence interval to use
DEFAULT_CI = 99

def get_output_dat_name(xaxis, alg, rev, index, num_verts):
    """Gets the name of an output file for a particular revision of an algorithm"""
    return DATA_PATH + '%s-%s-%u-%s-%s' % (xaxis, alg, index, rev, str(num_verts))

def make_latest(xaxis, alg, rev, index, num_verts):
    """Updates the symlink which points to the latest data file for an algorithm"""
    o = get_output_dat_name(xaxis, alg, rev, index, num_verts)
    linkname = DATA_PATH + 'latest/%s-%s-latest-%s' % (xaxis, alg, str(num_verts))
    quiet_remove(linkname)
    os.symlink(o, linkname)

def numeric_compare(a, b):
    if a < b:
        return -1
    elif b > a:
        return 1
    else:
        return 0

def density_compare(a, b):
    da = get_density(a)
    db = get_density(b)
    return numeric_compare(da, db)

def pom_compare(a, b):
    da = get_percent_of_max(a)
    db = get_percent_of_max(b)
    return numeric_compare(da, db)

def gather_perf_data(alg, rev, index, latest):
    """Gathers performance data for a single revision of an algorithm"""

    # get the results
    results = {} # maps (|V|, |E|) to ResultAccumulator
    ds = DataSet.read_from_file(PerfResult, PerfResult.get_path_to(rev))
    for data in ds.dataset.values():
        key = (data.input().num_verts, data.input().num_edges)
        result = results.get(key)
        if result is None:
            result = ResultAccumulator(data.time_sec)
            result.defaultCI = DEFAULT_CI
            results[key] = result
        else:
            result.add_data(data.time_sec)

    # put the results in order
    keys_density = results.keys()
    keys_density.sort(density_compare)
    keys_pom = results.keys()
    keys_pom.sort(pom_compare)
    keys = {}
    keys['density'] = keys_density
    keys['pom'] = keys_pom

    # compute stats for all the results
    for num_verts in results.keys():
        results[num_verts].compute_stats()

    # generate dat files for each x-axis cross important vertex counts
    for xaxis in keys:
        if xaxis == 'pom':
            computex = lambda v, e : get_percent_of_max(v, e)
        elif xaxis == 'density':
            computex = lambda v, e : get_density(v, e)
        else:
            print >> sys.stderr, "unexpected x-axis value: " + str(xaxis)
            sys.exit(-1)
        header_txt = '#|V|\t|E|\t' + xaxis + '\tLower\tAverage\tUpper\t#Runs  (Lower/Upper from ' + str(DEFAULT_CI) + '% CI)'

        for vip in IMPORTANT_VERTS:
            # open a file to output to
            dat = get_output_dat_name(xaxis, alg, rev, index, vip)
            if latest:
                make_latest(alg, rev, index, vip)
            try:
                fh = open(dat, 'w')

                # compute relevant stats and output them
                print >> fh, header_txt
                for (v, e) in keys:
                    if vip=='all' or vip==v:
                        r = results[(v, e)]
                        x = computex(v, e)
                        print >> fh, '%u\t%u\t%.6f\t%.3f\t%.3f\t%.3f\t%u' % (v, e, x, r.lower99, r.mean, r.upper99, len(r.values))
                fh.close()
            except IOError, e:
                print sys.stderr, "failed to write file: " + str(e)
                return -1
    return 0

def main():
    try:
        os.makedirs(DATA_PATH)
    except OSError:
        pass
    for alg in TRACKED.keys():
        revs = TRACKED[alg]
        for i in range(len(revs)):
            gather_perf_data(alg, revs[i], i, i+1==len(revs))

if __name__ == "__main__":
    sys.exit(main())
