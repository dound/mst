/**
 * Wrapper for the read_graph function.
 */

/* types of INPUT_TYPE */
#define SCANF 0
#define MMAP  1

/* use the default value for INPUT_TYPE if one is not specified */
#ifndef INPUT_TYPE
#  define INPUT_TYPE SCANF
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
 */
int read_graph(char *filename, int *n, int *m, edge **G);
