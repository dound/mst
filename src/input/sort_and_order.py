#!/usr/bin/env python

import sys

# simple script to order edges so that the lower index vertex is listed first
# and to put them in sorted order
def main(argv=sys.argv[1:]):
    fn = argv[0]
    try:
        fh = open(fn, mode='r')
    except IOError:
        print 'Unable to find', fn
        return -1

    lines = fh.readlines()
    for line in lines[:2]:
        print int(line)

    cmts = ''
    edges = []
    for line in lines[2:]:
        if line[0] == '#':
            cmts += line.rstrip()
            continue
        s = line.split()
        u = int(s[0])
        v = int(s[1])
        if u < v:
            edges.append((u, v, s[2]))
        else:
            edges.append((v, u, s[2]))

    fh.close()
    edges.sort()
    for (u, v, w) in edges:
        print u, v, w

    if len(cmts) > 0:
        print cmts

if __name__ == "__main__":
    sys.exit(main())
