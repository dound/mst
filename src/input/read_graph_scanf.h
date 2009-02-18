#include <input/adj_list.h> /* edge_list, AL_EDGE_LIST_* */
#include <input/adj_matrix.h> /* AM_INDEX */
#include <input/initialize_graph.h> /* initialize_* */
#include <input/pq_edge.h> /* pq_* */
#include <input/read_graph.h>
#include <stdio.h>  /* fopen, fscanf */
#include <mst.h> /* edge, foi */

// read input file, store results in n, m, and G
#if   GRAPH_TYPE == EDGE_LIST
int read_graph_to_edge_list_scanf(char *filename, int *n, int *m, edge **G)
#elif GRAPH_TYPE == HEAPIFIED_EDGE_LIST
int read_graph_to_heapified_edge_list_scanf(char *filename, int *n, int *m, edge **G)
#elif GRAPH_TYPE == ADJACENCY_LIST
int read_graph_to_adjacency_list_scanf(char *filename, int *n, int *m, edge_list **el)
#elif GRAPH_TYPE == ADJACENCY_MATRIX
int read_graph_to_adjacency_matrix_scanf(char *filename, int *n, int *m, foi **weights)
#else
#  error unknown GRAPH_TYPE
#endif
{
    FILE *input = fopen(filename, "r");
    fscanf(input, "%d", n);
    fscanf(input, "%d", m);

#if   GRAPH_TYPE == EDGE_LIST
    initialize_edge_list(G, *m);
#elif GRAPH_TYPE == HEAPIFIED_EDGE_LIST
    pq_init(*m);
    *G = pq;
#elif GRAPH_TYPE == ADJACENCY_LIST
    initialize_adjacency_list(el, *n, *m);
#elif GRAPH_TYPE == ADJACENCY_MATRIX
    initialize_adjacency_matrix(weights, *n);
#endif
#if GRAPH_TYPE == ADJACENCY_LIST || GRAPH_TYPE == ADJACENCY_MATRIX
    int u, v;
    foi w;
#endif
#ifdef _NO_FLOATS_
    int tmp;
#endif

    int i = 0;
    int charsRead = 1;
#if GRAPH_TYPE == HEAPIFIED_EDGE_LIST
    for (i = 1; i < *m+1; i++)
#else
    for (i = 0; i < *m; i++)
#endif
    {
#if GRAPH_TYPE == EDGE_LIST || GRAPH_TYPE == HEAPIFIED_EDGE_LIST
#   ifdef _NO_FLOATS_
        charsRead = fscanf(input, "%d %d %d.%d",
                           &(*G)[i].u, &(*G)[i].v, &(*G)[i].weight, &tmp);
        (*G)[i].weight = (*G)[i].weight * 10 + tmp;
#   else
        charsRead = fscanf(input, "%d %d %f",
                           &(*G)[i].u, &(*G)[i].v, &(*G)[i].weight);
#   endif
#   if GRAPH_TYPE == HEAPIFIED_EDGE_LIST
        pq_heapify_insertion(); /* maintain the heap property */
#   endif
#elif GRAPH_TYPE == ADJACENCY_LIST || GRAPH_TYPE == ADJACENCY_MATRIX
#   ifdef _NO_FLOATS_
        charsRead = fscanf(input, "%d %d %d.%d", &u, &v, &w, &tmp);
        w = w * 10 + tmp;
#   else
        charsRead = fscanf(input, "%d %d %f", &u, &v, &w);
#   endif
#   if GRAPH_TYPE == ADJACENCY_LIST
        AL_EDGE_LIST_ADD(&(*el)[u], v, w);
        AL_EDGE_LIST_ADD(&(*el)[v], u, w);
#   elif GRAPH_TYPE == ADJACENCY_MATRIX
        (*weights)[AM_INDEX(*n,u,v)] = w;
#   endif
#endif

        if (charsRead == EOF) {
            printf("premature EOF in input\n");
            return 0;
        }
    }

    return 1;
}
