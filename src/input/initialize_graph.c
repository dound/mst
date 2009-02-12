#include <stdlib.h> /* malloc */
#include <input/initialize_graph.h>

void initialize_edge_list(edge **G, int num_edges) {
    *G = (edge *)malloc(num_edges * sizeof(edge));
}

void initialize_adjacency_list(void **G, int num_verts) {
    *G = NULL; /* not yet implemented */
}

void initialize_adjacency_matrix(float **G, int num_verts) {
    float *weights = *G = (float*)malloc(num_verts * num_verts * sizeof(float));
    for(int i=0; i<num_verts*num_verts; i++)
        weights[i] = -1.0f;
}
