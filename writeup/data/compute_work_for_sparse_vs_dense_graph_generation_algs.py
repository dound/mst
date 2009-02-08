#!/usr/bin/env python

import math

# Purpose: Generate data for a plot of dense and spark work (y) for a range of
# edge densities (x).
#
# Output: each row is: x

# Density range
DATAROW_FORMAT = '%.3f\t%.0f\t%.0f\t%.0f'
DENSITY_STEP = .01
DENSITY_MIN  = 0.0  # symbolizes V - 1
DENSITY_MAX  = 1.0  # symbolizes V * (V - 1) / 2
NUM_STEPS = int((DENSITY_MAX - DENSITY_MIN) / DENSITY_STEP)

# Vertex range (crossover point is actually independent of num_verts!)
VERTS_MIN = 128
VERTS_STEP_MULTIPLIER = 4
VERTS_NUM_STEPS = 6

def compute_dense_work(v, e):
    return v * v * math.log(v * v, 2)

def compute_sparse_work(v, e, fast_but_overestimate=False, step=1):
    v = float(v)

    if fast_but_overestimate:
        return e * (v * v - v) / (v * v - v - 2 * e) # treat every edge like the last edge
    else:
        sum_etries = 0
        denom = (v * v - v) / 2
        for i in range(0, int(e), step):
            psuccess = 1 - i / denom             # chance we'll choose a free edge at this point
            sum_etries += step * (1 / psuccess)  # num tries we expect to do to get step free edges
        return sum_etries

# number of edges to approximate cost for at once (higher => slightly less accurate, but faster
qstep = 1

for vert_step_num in range(0, VERTS_NUM_STEPS):
    mult = VERTS_STEP_MULTIPLIER**vert_step_num
    qstep = mult
    num_verts = VERTS_MIN * mult
    min_e = num_verts - 1
    max_e = num_verts * (num_verts - 1) / 2

    out = open('work_for_sparse_vs_dense_graph_generation_algs-%u.dat' % num_verts, "w")
    print >> out, '#Density%\tSparseWorkHigh\tSparseWorkTight\tDenseWork'

    d = DENSITY_MIN
    for step_num in range(0, NUM_STEPS):
        print 'd_on = ' + str(d)

        # linearly interpolate between no density (spanning tree) and full density (complete graph)
        num_edges = (1.0 - d)*min_e + d*max_e

        # compute the work for both algs
        ideal_fraction_of_complete = 2 * num_edges / (num_verts * (num_verts - 1))
        dense_work = compute_dense_work(num_verts, num_edges)
        sparse_work_high = compute_sparse_work(num_verts, num_edges, True)
        sparse_work_tight = compute_sparse_work(num_verts, num_edges, False, qstep)

        # print the data for this density and then go on to the next density
        print >> out, DATAROW_FORMAT % (d, sparse_work_high, sparse_work_tight, dense_work)
        d += DENSITY_STEP

    out.close()
