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

def get_edges_from_percent_of_max(num_verts, pom):
    """Determine how many edges are in a graph given |V| and the percent of max."""
    return (num_verts - 1) * (num_verts * pom - 2 * pom + 2) / 2.0

# how many versions of each variation to try
num_versions = 5

# compute which |V| values we want to use
vertices = [250, 700, 4473]

# compute which percent of max ratios we want to use
poms = [.03, .05, .95] + [p / 100.0 for p in inclusive_range(10, 100, 10)]
poms.sort()

# compute the cross-product
num_vars = len(vertices)*len(poms)
print 'adding %u |V| values and %u poms for a total of %u variations:' % (len(vertices), len(poms), num_vars)
print '   vertices:  ' + str(vertices)
print '   poms: ' + str(poms)
variations = []
for v in vertices:
    for p in poms:
        e = int(get_edges_from_percent_of_max(v, p))
        density = e / float(v)
        if density > 55 and density < 135 and v < 500:
            what = 'skipped: '
        else:
            what = 'added: '
            variations.append( (e, v) )
        print '%sv=%u pom=%.2f e=%u => density=%.2f' % (what, v, p, e, e/float(v))

# compute expected size
tot_sz = 0
max_sz = 0
for (e, v) in variations:
    # per edge size cost is chars for two vertices, an edge weight, and spacing
    my_sz = (e * (2 * len(str(v)) + 8 + 3))
    max_sz = max(max_sz, my_sz)
    tot_sz += my_sz

tot_sz /= (1024 * 1024)
max_sz /= (1024 * 1024)
print 'aggregate input size is %uMB (max input file size is %uMB)' % (int(tot_sz), int(max_sz))

# generate the graphs
for i in range(1, num_versions+1):
    ifl = get_path_to_project_root() + 'input/cperf-%u.inputs' % i
    print 'generating inputs for ' + ifl
    for (e, v) in variations:
        argstr = '--dont-generate -q -l %s -n %u %u' % (ifl, e, v)
        generate_input(argstr.split())
