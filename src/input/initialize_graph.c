#include <stdlib.h> /* malloc */
#include <input/adj_list.h> /* edge_list, edge_to, EDGE_LIST_* */
#include <input/adj_matrix.h> /* AM_NO_EDGE */
#include <input/initialize_graph.h>
#include <mst.h> /* edge, foi */
#include <string.h> /* memset */

void initialize_edge_list(edge **G, int num_edges) {
    *G = (edge *)malloc(num_edges * sizeof(edge));
}

void initialize_adjacency_list(edge_list **el, int num_verts, int num_edges) {
    /* index 0 is ignored => access easier (verts start at index 1) */
    *el = (edge_list*)malloc((num_verts+1) * sizeof(edge_list));
#ifdef _DEBUG_
    memset(*el, 0xFF, sizeof(edge_list)); /* ensure data at index 0 is junk */
#endif
#if AL_TYPE == AL_VECTORS
    /* multiply by two because we track edges in both directions */
    int num_initial_edges = (2 * num_edges) / num_verts;
    for(int i=1; i<=num_verts; i++) {
        edge_list *e = &(*el)[i];
        e->used = 0;
        e->avail = num_initial_edges;
        e->a = malloc(e->avail * sizeof(edge_to));
    }
#elif AL_TYPE == AL_LL
    for(int i=1; i<=num_verts; i++)
        (*el)[i].head = NULL;
#else
#   error unknown AL_TYPE
#endif
}

void initialize_adjacency_matrix(foi **G, int num_verts) {
    foi *weights = *G = (foi*)malloc(num_verts * num_verts * sizeof(foi));
    for(int i=0; i<num_verts*num_verts; i++)
        weights[i] = AM_NO_EDGE;
}
