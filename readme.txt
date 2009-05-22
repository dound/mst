An optimized library of minimum spanning tree algorithms.  Includes various
implementations of Kruskal's and Prim's algorithms in the C programming
language.  This implementation outperforms the boost library's implementation on
a variety of graph sizes and types.

This work was done by David Underhill and Derrick Isaacson for Tim Roughgarden's
Algorithms class at Stanford University during the Winter 2009 quarter.  It won
first place in the class-wide competition by a good margin.

The library necessarily implements efficient data structures for graphs including
an adjacency matrix, adjacency list, heapified edge list, or plain edge list.
It also provides fast methods for reading graphs from an ASCII-based text file
(both scanf-based and memory-mapped I/O).

To maximize compiler optimization opportunities, some choices can only be
specified by compile-define macros.  These macros are documented in
src/doc/macro-defines.txt.

This library depends only on the standard C library.  It includes about 2100
lines of C code.  It also includes an extensive test suite, written in about
3000 lines of Python code, which we used to help guide our optimization efforts.
