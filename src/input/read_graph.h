/**
 * Wrapper for the read_graph function.
 */
#ifndef READ_GRAPH_H
#define READ_GRAPH_H

#include <input/adj_list.h> /* edge_list */
#include <mst.h> /* edge, foi */

/* INPUT_TYPE: ways to read in a graph */
#define SCANF 1
#define MMAP  2

/* use the default value for INPUT_TYPE if one is not specified */
#ifndef INPUT_TYPE
#  define INPUT_TYPE MMAP
#endif

/* GRAPH_TYPE: types of graph outputs */
#define EDGE_LIST           1
#define HEAPIFIED_EDGE_LIST 2
#define ADJACENCY_LIST      3
#define ADJACENCY_MATRIX    4

/* apply INPUT_TYPE */
#if INPUT_TYPE == SCANF
#  define read_graph_to_edge_list read_graph_to_edge_list_scanf
#  define read_graph_to_heapified_edge_list read_graph_to_heapified_edge_list_scanf
#  define read_graph_to_adjacency_list read_graph_to_adjacency_list_scanf
#  define read_graph_to_adjacency_matrix read_graph_to_adjacency_matrix_scanf
#elif INPUT_TYPE == MMAP
#  define read_graph_to_edge_list read_graph_to_edge_list_mmap
#  define read_graph_to_heapified_edge_list read_graph_to_heapified_edge_list_mmap
#  define read_graph_to_adjacency_list read_graph_to_adjacency_list_mmap
#  define read_graph_to_adjacency_matrix read_graph_to_adjacency_matrix_mmap
#else
#  error bad argument to INPUT_TYPE
#endif

/**
 * Reads in a graph from filename into a data structure which is simply a list
 * of edges.  Returns via passed arguments the number of vertices (n), number
 * edges (m), and edges in the graph (G).
 *
 * The implementation of this method depends on the INPUT_TYPE macro.
 *
 * @return 1 on success, 0 on failure
 */
int read_graph_to_edge_list(char *filename, int *n, int *m, edge **G);

/**
 * Reads in a graph from filename into a heap data structure.  Returns via
 * passed arguments the number of vertices (n), number edges (m), and edges in
 * the graph (G).
 *
 * The implementation of this method depends on the INPUT_TYPE macro.
 *
 * @return 1 on success, 0 on failure
 */
int read_graph_to_heapified_edge_list(char *filename, int *n, int *m, edge **G);

/**
 * Reads in a graph from filename into an adjancency list representation.
 * Returns via passed arguments the number of vertices (n), number edges (m),
 * and TBD in the graph (G).
 *
 * The implementation of this method depends on the INPUT_TYPE macro.
 *
 * @return 1 on success, 0 on failure
 */
int read_graph_to_adjacency_list(char *filename, int *n, int *m, edge_list **el);

/**
 * Reads in a graph from filename into an adjancency matrix representation.
 * Returns via passed arguments the number of vertices (n), number edges (m),
 * and weights between all vertices in the graph (weights).
 *
 * The implementation of this method depends on the INPUT_TYPE macro.
 *
 * @return 1 on success, 0 on failure
 */
int read_graph_to_adjacency_matrix(char *filename, int *n, int *m, foi **weights);

#endif /* READ_GRAPH_H */

