#!/usr/bin/env python

import sys

# simple script to order edges so that the lower index vertex is listed first
# and to put them in sorted order
def main(argv=sys.argv[1:]):
    if len(argv) == 0:
        print 'usage: FILE [NUM_LINES_TO_SKIP]'
        sys.exit(0)

    if len(argv) == 2:
        num_lines_to_skip = int(argv[1])
    else:
        num_lines_to_skip = 0

    fn = argv[0]
    try:
        fh = open(fn, mode='r')
    except IOError:
        print 'Unable to find', fn
        return -1


    cmts = ''
    edges = []
    lines = fh.readlines()[num_lines_to_skip:]
    for line in lines:
        # ignore comments until the end
        if line[0] == '#':
            cmts += line.rstrip()
            continue

        s = line.split()

        # just print header lines back out as-is
        if len(s) == 1:
            print line.rstrip()
            continue

        # save vertex-vertex[-weight] lines for later, with u < v
        u = int(s[0])
        v = int(s[1])
        if len(s) == 2:
            if u < v:
                edges.append((u, v))
            else:
                edges.append((v, u))
        else:
            if u < v:
                edges.append((u, v, s[2]))
            else:
                edges.append((v, u, s[2]))


    fh.close()

    # print the vertex-vertex[-weight] lines in sorted order
    edges.sort()
    for t in edges:
        print "".join([str(s)+' ' for s in t])

    if len(cmts) > 0:
        print cmts

if __name__ == "__main__":
    sys.exit(main())
