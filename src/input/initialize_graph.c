#include <stdlib.h> /* malloc */
#include <input/adj_matrix.h> /* AM_NO_EDGE */
#include <input/initialize_graph.h>
#include <mst.h> /* edge, foi */

void initialize_edge_list(edge **G, int num_edges) {
    *G = (edge *)malloc(num_edges * sizeof(edge));
}

void initialize_adjacency_list(void **G, int num_verts) {
    *G = NULL; /* not yet implemented */
}

void initialize_adjacency_matrix(foi **G, int num_verts) {
    foi *weights = *G = (foi*)malloc(num_verts * num_verts * sizeof(foi));
    for(int i=0; i<num_verts*num_verts; i++)
        weights[i] = AM_NO_EDGE;
}
