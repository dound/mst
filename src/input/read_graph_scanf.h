#include <input/adj_matrix.h> /* AM_INDEX */
#include <input/initialize_graph.h> /* initialize_* */
#include <stdio.h>  /* fopen, fscanf */
#include <mst.h> /* edge */

// read input file, store results in n, m, and G
#if   GRAPH_TYPE == EDGE_LIST
int read_graph_to_edge_list_scanf(char *filename, int *n, int *m, edge **G)
#elif GRAPH_TYPE == ADJACENCY_LIST
int read_graph_to_adjacency_list_scanf(char *filename, int *n, int *m, void **G)
#elif GRAPH_TYPE == ADJACENCY_MATRIX
int read_graph_to_adjacency_matrix_scanf(char *filename, int *n, int *m, float **weights)
#else
#  error unknown GRAPH_TYPE
#endif
{
    FILE *input = fopen(filename, "r");
    fscanf(input, "%d", n);
    fscanf(input, "%d", m);

#if   GRAPH_TYPE == EDGE_LIST
    initialize_edge_list(G, *m);
#elif GRAPH_TYPE == ADJACENCY_LIST
    initialize_adjacency_list(G, *n);
#elif GRAPH_TYPE == ADJACENCY_MATRIX
    initialize_adjacency_matrix(weights, *n);
    int u, v;
    float w;
#endif

    int i = 0;
    int charsRead = 1;
    for (i = 0; i < *m; i++)
    {
#if   GRAPH_TYPE == EDGE_LIST
        charsRead = fscanf(input, "%d %d %f",
                           &(*G)[i].u, &(*G)[i].v, &(*G)[i].weight);
#elif GRAPH_TYPE == ADJACENCY_LIST
                           /* not yet implemented */
#elif GRAPH_TYPE == ADJACENCY_MATRIX
        charsRead = fscanf(input, "%d %d %f", &u, &v, &w);
        (*weights)[AM_INDEX(*n,u,v)] = w;
#endif

        if (charsRead == EOF) {
            printf("premature EOF in input\n");
            return 0;
        }
    }

    return 1;
}
