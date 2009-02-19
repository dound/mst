#!/usr/bin/env python

from generate_input import edges_in_complete_undirected_graph, main as generate_input
from math import ceil, sqrt
from mstutil import get_path_to_project_root

def inclusive_range(min_val, max_val, step):
    ret = range(min_val, max_val, step)
    if ret[len(ret) - 1] != max_val:
        ret.append(max_val)
    return ret

def vertices_in_complete_undirected_graph(num_edges):
    return (sqrt(8.0 * num_edges + 1.0) + 1.0) / 2.0

# how many versions of each variation to try
num_versions = 5

# compute which |E| values we want to use
small_edges = inclusive_range( 100 * 1000,       600 * 1000,  100 * 1000)
large_edges = inclusive_range(1000 * 1000, 10 * 1000 * 1000, 1000 * 1000)
edges = small_edges + large_edges

# compute which |E|/|V| ratios we want to use
sparse_ratios = [5, 50] #inclusive_range(5, 50, 5)
dense_ratios = [150, 1500] #inclusive_range(150, 1500, 150)
ratios = sparse_ratios + dense_ratios

# compute the cross-product of |E| and the ratios
num_vars = len(edges)*len(ratios)
print 'considering %u |E| values and %u ratios for a total of %u variations:' % (len(edges), len(ratios), num_vars)
print '   edges:  ' + str(edges)
print '   ratios: ' + str(ratios)
variations = []
for e in edges:
    for r in ratios:
        v = (1.0 / r) * e
        v = int(v)
        max_edges = edges_in_complete_undirected_graph(v)
        if e < max_edges:
            variations.append( (e, v) )
fmt = 'got %u variations, now adding %u complete graphs for a total of %u variations'
print fmt % (len(variations), len(edges), len(variations) + len(edges))

# add the complete graphs
for e in edges:
    v = ceil(vertices_in_complete_undirected_graph(e))
    e = edges_in_complete_undirected_graph(v)
    variations.append( (e, v) )

# compute expected size
tot_sz = 0
max_sz = 0
for (e, v) in variations:
    # per edge size cost is chars for two vertices, an edge weight, and spacing
    my_sz = (e * (2 * len(str(v)) + 8 + 3))
    max_sz = max(max_sz, my_sz)
    tot_sz += my_sz

tot_sz /= (1024 * 1024 * 1024)
max_sz /= (1024 * 1024)
print 'aggregate input size is %uGB (max input file size is %uMB)' % (int(tot_sz), int(max_sz))

# generate the graphs
for i in range(1, num_versions+1):
    ifl = get_path_to_project_root() + 'input/nperf-%u.inputs' % i
    print 'generating inputs for ' + ifl
    for (e, v) in variations:
        argstr = '--dont-generate -q -l %s -n %u %u' % (ifl, e, v)
        generate_input(argstr.split())
