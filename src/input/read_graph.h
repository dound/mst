/**
 * Wrapper for the read_graph function.
 */
#ifndef READ_GRAPH_H
#define READ_GRAPH_H

/* types of INPUT_TYPE */
#define SCANF 0
#define MMAP  1

/* use the default value for INPUT_TYPE if one is not specified */
#ifndef INPUT_TYPE
#  define INPUT_TYPE MMAP
#endif

/* apply INPUT_TYPE */
#if INPUT_TYPE == SCANF
#  define read_graph read_graph_scanf
#  include "read_graph_scanf.h"
#elif INPUT_TYPE == MMAP
#  define read_graph read_graph_mmap
#  include "read_graph_mmap.h"
#else
#  error bad argument to 'INPUT_TYPE': INPUT_TYPE
#endif

/**
 * Reads in a graph from filename.  Returns via passed arguments the number of
 * vertices (n), number edges (m), and edges in the graph (G).
 *
 * The implementation of this method depends on the INPUT_TYPE macro.
 *
 * @return 1 on success, 0 on failure
 */
int read_graph(char *filename, int *n, int *m, edge **G);

#endif /* READ_GRAPH_H */
